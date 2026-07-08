"""A configurable dynamic-range compressor — the design decision map as code.

Every keyword argument of `compress()` is one row of the compressor design
decision map (see research/compressor-design-decisions.md and the interactive
figure on the Visualizations page). Choosing one option per decision traces a
path from "no design" to a complete compressor; this one engine plays all the
valid paths. The five open-source reference implementations analyzed in
`thirdparty/compare/analysis.md` are included as PRESETS.

Pure standard library, offline, mono, teaching code — not production DSP.
Signals are plain Python lists of floats in [-1.0, 1.0]; levels are dBFS
(peak detection per sample unless detector="rms"). See the Conventions page.

Where the code narrows the map:

* knee="soft_curve" (sox's Bezier joint) is not a separate function: for a
  single knee, a quadratic Bezier whose control point sits at the hard-knee
  corner evaluates to the same tangent parabola as knee="soft_quad". Sox's
  real generality is *multi-segment* user-defined curves, out of scope here.
  The sox preset therefore uses soft_quad.
* The map's smoothing "none" (pcs) is expressed as ballistics="none".
* ballistics="program" (program-dependent release) is deliberately not
  implemented. Sketch: track how transient the material is (e.g. the recent
  peak/RMS crest factor, or how long the level has sat above threshold) and
  blend between a fast and a slow release constant accordingly; punchy
  material gets the fast release, sustained material the slow one. None of
  the five reference implementations do this, and a rigorous version needs
  listening tests — so it stays prose for now.

Not every path composes (a fact the map itself doesn't show):

* topology="feedback" cannot be combined with lookahead — you cannot look
  ahead at output you have not produced yet. `compress()` raises ValueError.
"""

import math
from collections import deque

# --------------------------------------------------------------------------
# Conversions (identical to the Conventions page)
# --------------------------------------------------------------------------

def db_from_amplitude(a):
    """Linear amplitude -> dBFS. Zero amplitude maps to -inf."""
    a = abs(a)
    return 20.0 * math.log10(a) if a > 0.0 else float("-inf")


def amplitude_from_db(db):
    """dBFS -> linear amplitude."""
    return 10.0 ** (db / 20.0)


# --------------------------------------------------------------------------
# Decision: knee -- (overshoot_db, ratio, knee_db) -> gain reduction in dB (<= 0)
#
# `over` is the detected level minus the threshold, in dB. All three return 0
# for signals safely below the knee and slope*over far above it, where
# slope = 1/ratio - 1 (negative; ratio=math.inf gives slope -1, a limiter).
# --------------------------------------------------------------------------

def knee_hard(over, ratio, knee_db):
    """Two straight lines meeting at the threshold (dafx-style `min`)."""
    if over <= 0.0:
        return 0.0
    return (1.0 / ratio - 1.0) * over


def knee_soft_quad(over, ratio, knee_db):
    """Quadratic gain spline straddling the threshold (audacity/Rudrich).

    A parabola on over in [-knee/2, +knee/2] that is *tangent* to both
    straight segments: the characteristic's slope is continuous (C1).
    """
    if knee_db <= 0.0:
        return knee_hard(over, ratio, knee_db)
    slope = 1.0 / ratio - 1.0
    half = knee_db / 2.0
    if over <= -half:
        return 0.0
    if over >= half:
        return slope * over
    return 0.5 * slope * (over + half) * (over + half) / knee_db


def knee_soft_linear(over, ratio, knee_db):
    """Linear ratio blend across the knee (guitarix-style).

    The *ratio* is interpolated linearly over [threshold, threshold+knee],
    then applied. Continuous in value, but the slope jumps at the knee's
    upper edge (C0, not C1) -- the audible/mathematical difference from
    knee_soft_quad, and exactly the kink noted in compare/analysis.md.
    """
    if over <= 0.0:
        return 0.0
    if knee_db <= 0.0 or over >= knee_db:
        return (1.0 / ratio - 1.0) * over
    p = over / knee_db                      # 0..1 across the knee
    r_eff = 1.0 + p * (ratio - 1.0)         # 1 -> ratio
    return (1.0 / r_eff - 1.0) * over


KNEES = {
    "hard": knee_hard,
    "soft_linear": knee_soft_linear,
    "soft_quad": knee_soft_quad,
}

# --------------------------------------------------------------------------
# Decision: ballistics -- one-pole attack/release smoothing
# --------------------------------------------------------------------------

def smoothing_coeff(time_ms, sr):
    """One-pole coefficient for a time constant at sample rate sr."""
    if time_ms <= 0.0:
        return 0.0                          # snap instantly
    return math.exp(-1.0 / (sr * time_ms / 1000.0))


def _smooth(env, target, atk, rel, attack_when_rising):
    """Move env toward target: attack coefficient in the effect's 'grab'
    direction, release in the 'let go' direction. For a *level* envelope the
    grab direction is rising; for a *gain-reduction* envelope it is falling
    (more negative = clamping harder)."""
    rising = target > env
    coeff = atk if rising == attack_when_rising else rel
    return coeff * env + (1.0 - coeff) * target


# --------------------------------------------------------------------------
# Lookahead helper: sliding minimum over the next `width` values.
# Reduction is <= 0 dB, so the minimum is the *deepest* upcoming reduction:
# the gain is pre-armed so it is already in place when the transient lands.
# (A teaching-scale version of audacity's reverse-scan pre-ramp.)
# --------------------------------------------------------------------------

def _sliding_min(values, width):
    """out[n] = min(values[n : n+width]), O(n) via a monotonic deque."""
    n = len(values)
    out = [0.0] * n
    dq = deque()                            # indices with increasing values
    j = 0                                   # next index to admit
    for i in range(n):
        hi = min(i + width - 1, n - 1)
        while j <= hi:
            while dq and values[dq[-1]] >= values[j]:
                dq.pop()
            dq.append(j)
            j += 1
        while dq[0] < i:
            dq.popleft()
        out[i] = values[dq[0]]
    return out


# --------------------------------------------------------------------------
# The engine
# --------------------------------------------------------------------------

_CHOICES = {
    "detector": ("peak", "rms"),
    "topology": ("feedforward", "feedback"),
    "knee": tuple(KNEES),
    "smoothing": ("before", "after"),
    "ballistics": ("none", "fixed"),
    "lookahead": ("none", "delay", "true"),
    "makeup": ("manual", "auto"),
}


def compress(x, sr, *,
             threshold_db=-20.0, ratio=4.0, knee_db=6.0,
             detector="peak", topology="feedforward", knee="hard",
             smoothing="after", ballistics="fixed",
             attack_ms=5.0, release_ms=50.0, rms_ms=10.0,
             lookahead="none", lookahead_ms=5.0,
             makeup="manual", makeup_db=0.0):
    """Run the configurable compressor over mono samples `x` at rate `sr`.

    Each keyword is one decision from the design map:

    detector    "peak" (per-sample |x|) or "rms" (one-pole mean-square,
                window ~rms_ms).
    topology    "feedforward" (detect the input) or "feedback" (detect the
                previous *output* sample).
    knee        "hard", "soft_linear" (kinked ratio blend), or "soft_quad"
                (tangent parabola). Width = knee_db.
    smoothing   Where the ballistics sit: "before" smooths the detected
                *level* (linear domain); "after" smooths the computed *gain
                reduction* (dB domain).
    ballistics  "fixed" one-pole attack/release, or "none" (snap -- the pcs
                behavior). "program" is sketched in the module docstring
                only.
    lookahead   "none"; "delay" (delay the audio so the gain computed from
                the undelayed detector lands time-aligned); "true" (also
                pre-arm the gain with the deepest reduction in the next
                window, so peaks cannot overshoot). Latency = lookahead_ms.
    makeup      "manual" (use makeup_db) or "auto" (cancel the reduction a
                0 dBFS input would get -- one common convention).

    Returns a new list, same length as x. Lookahead modes delay the output
    by round(sr * lookahead_ms / 1000) samples.
    """
    for name, value in (("detector", detector), ("topology", topology),
                        ("knee", knee), ("smoothing", smoothing),
                        ("ballistics", ballistics), ("lookahead", lookahead),
                        ("makeup", makeup)):
        if value not in _CHOICES[name]:
            raise ValueError(f"{name}={value!r}: choose from {_CHOICES[name]}")
    if topology == "feedback" and lookahead != "none":
        raise ValueError("feedback topology cannot look ahead at output "
                         "that does not exist yet: use topology='feedforward' "
                         "or lookahead='none'")

    knee_fn = KNEES[knee]
    atk = smoothing_coeff(attack_ms, sr)
    rel = smoothing_coeff(release_ms, sr)
    rms_coeff = smoothing_coeff(rms_ms, sr)
    if ballistics == "none":
        atk = rel = 0.0                     # snap: no time behavior

    if makeup == "auto":
        # Cancel the reduction a full-scale (0 dBFS) input would receive.
        makeup_db = -knee_fn(0.0 - threshold_db, ratio, knee_db)

    if topology == "feedback":
        return _run_feedback(x, knee_fn, threshold_db, ratio, knee_db,
                             detector, smoothing, atk, rel, rms_coeff,
                             makeup_db)
    delay = 0
    if lookahead != "none":
        delay = int(round(sr * lookahead_ms / 1000.0))
    return _run_feedforward(x, knee_fn, threshold_db, ratio, knee_db,
                            detector, smoothing, atk, rel, rms_coeff,
                            makeup_db, lookahead, delay)


def _detect(sample, detector, ms_state, rms_coeff):
    """One detector step. Returns (linear level, new mean-square state)."""
    if detector == "rms":
        ms_state = rms_coeff * ms_state + (1.0 - rms_coeff) * sample * sample
        return math.sqrt(ms_state), ms_state
    return abs(sample), ms_state


def _run_feedforward(x, knee_fn, threshold_db, ratio, knee_db,
                     detector, smoothing, atk, rel, rms_coeff,
                     makeup_db, lookahead, delay):
    # Pass 1: per-sample gain-reduction targets from the (undelayed) input.
    targets = []
    ms = 0.0
    env_level = 0.0
    for s in x:
        level, ms = _detect(s, detector, ms, rms_coeff)
        if smoothing == "before":           # smooth the detected level
            env_level = _smooth(env_level, level, atk, rel,
                                attack_when_rising=True)
            level = env_level
        over = db_from_amplitude(level) - threshold_db
        targets.append(knee_fn(over, ratio, knee_db))

    # True lookahead: the gain at output step n is applied to the *delayed*
    # sample x[n-delay], so it must be pre-armed with the deepest reduction
    # over that sample's window [n-delay .. n] -- the emitted sample through
    # the newest analyzed input. (Anchoring the window to the input clock
    # instead lets the tail of a burst escape as the detector sees quiet
    # future samples -- a bug the tests catch.)
    if lookahead == "true" and delay > 0:
        slid = _sliding_min(targets, delay + 1)   # slid[m] = min(targets[m..m+delay])
        targets = [slid[n - delay] if n >= delay else slid[0]
                   for n in range(len(slid))]

    # Pass 2: smooth (if smoothing="after") and apply, to the delayed signal.
    y = []
    env_red = 0.0
    for n, target in enumerate(targets):
        if smoothing == "after":            # smooth the gain reduction
            env_red = _smooth(env_red, target, atk, rel,
                              attack_when_rising=False)
            red = env_red
        else:
            red = target
        gain = amplitude_from_db(red + makeup_db)
        src = x[n - delay] if n >= delay else 0.0
        y.append(src * gain)
    return y


def _run_feedback(x, knee_fn, threshold_db, ratio, knee_db,
                  detector, smoothing, atk, rel, rms_coeff, makeup_db):
    # Single pass: the detector reads the *previous output* sample, so the
    # loop regulates itself (one-sample feedback delay, the digital analogue
    # of an analogue feedback compressor). No lookahead is possible.
    y = []
    ms = 0.0
    env_level = 0.0
    env_red = 0.0
    y_prev = 0.0
    for s in x:
        level, ms = _detect(y_prev, detector, ms, rms_coeff)
        if smoothing == "before":
            env_level = _smooth(env_level, level, atk, rel,
                                attack_when_rising=True)
            level = env_level
        over = db_from_amplitude(level) - threshold_db
        target = knee_fn(over, ratio, knee_db)
        if smoothing == "after":
            env_red = _smooth(env_red, target, atk, rel,
                              attack_when_rising=False)
            red = env_red
        else:
            red = target
        y_prev = s * amplitude_from_db(red + makeup_db)
        y.append(y_prev)
    return y


# --------------------------------------------------------------------------
# The five reference implementations as paths through the map.
# Adapted from thirdparty/compare/analysis.md; parameter values are
# representative defaults, not transcriptions. sox uses soft_quad -- see the
# module docstring for why its Bezier knee collapses to the same parabola.
# --------------------------------------------------------------------------

PRESETS = {
    "dafx":     dict(detector="rms",  topology="feedforward", knee="hard",
                     smoothing="after",  ballistics="fixed",
                     lookahead="delay", makeup="manual"),
    "pcs":      dict(detector="rms",  topology="feedforward", knee="hard",
                     smoothing="after",  ballistics="none",
                     lookahead="none",  makeup="auto"),
    "guitarix": dict(detector="peak", topology="feedforward", knee="soft_linear",
                     smoothing="before", ballistics="fixed",
                     lookahead="none",  makeup="manual"),
    "sox":      dict(detector="peak", topology="feedforward", knee="soft_quad",
                     smoothing="before", ballistics="fixed",
                     lookahead="delay", makeup="manual"),
    "audacity": dict(detector="peak", topology="feedforward", knee="soft_quad",
                     smoothing="after",  ballistics="fixed",
                     lookahead="true",  makeup="manual"),
}
