# Automatic Gain Control

> Automatic gain control (AGC) holds a signal's level near a chosen target, correcting
> slow drift without reshaping the moment-to-moment dynamics.

*Chapter 6 — companding. The slow, transparent member of the family; builds on
[Measuring sound](conventions.md) and the envelope follower of
[Chapter 5](envelopes.md).*

---

## Intuition

AGC behaves like an engineer riding a fader during a panel discussion: one guest leans in
and booms, another sits back and murmurs, and the fader moves over seconds to keep both at
an even level without chasing individual syllables. AGC automates that slow hand.

Typical uses: a lavalier microphone on a presenter who turns their head, a recording whose
source drifts over minutes, a voice chat where every participant should arrive at the
listener at the same level.

!!! note "Is AGC an effect, a technique, or a goal?"
    Mostly a goal, realized as a control technique, and only loosely an effect. Unlike a
    compressor, there is no single canonical AGC algorithm; the name describes an
    objective — hold the output near a target — rather than one transfer function. In
    practice it is built as a slow feedback loop from familiar primitives, a level
    detector ([Chapter 2](conventions.md)) and a one-pole follower
    ([Chapter 5](envelopes.md)), wired to seek a target instead of applying a fixed curve.

## Key parameters

| Parameter | What it controls |
|---|---|
| Target level | The level (dBFS) the loop drives the output toward. |
| Time constant | How fast the loop corrects. Slow (about 1 s or more) keeps it transparent; faster settings turn it into a leveler or limiter. |
| Max gain | A ceiling on the boost, so quiet passages and noise are not over-amplified. |
| Noise floor | A level below which the loop stops adapting, so silence is not pumped up. |

## How it works

AGC is a closed feedback loop. Each sample:

1. Apply the current gain to the input, producing the output sample.
2. Measure the output level: smooth the output's magnitude into an envelope and convert to
   dBFS. This is the feedback: the loop watches its own output, not the input.
3. Compare with the target: `error = target − measured_level`.
4. Nudge the gain slowly toward closing the error (a slow integrator), clamped to the max
   gain, and paused while the signal is below the noise floor.

Because the loop is slow, it flattens long-term drift and leaves short-term dynamics
essentially untouched.

### Where AGC sits among its cousins

AGC, limiting, and compression are the same level-control machinery at different settings.
Following Woodgate (ISCVE Engineering Note 27.1, anchored to IEC 60268-8), they separate
on two axes: how hard they hold the output flat, and how fast they react.

| | Output held ~constant | Output less-than-proportional |
|---|---|---|
| Slow release (≈1 s+) | AGC — transparent | — |
| Fast release (~ms) | Limiting — audible | Compression — audible |

The dividing line: correctly implemented AGC does not change the subjective quality of the
program, while compression and limiting deliberately do. The distinction is corrective
versus creative.

On a steady-state transfer curve, AGC and a limiter draw the same flattened line; the
separator, release time, only shows in the time domain. The
[Visualizations](visualizations.md) appendix has an interactive figure of this.

## Pseudocode

```text
gain_db = 0
for each sample x:
    y     = x * dB_to_linear(gain_db)        # apply current gain
    level = dBFS(smoothed |y|)               # measure the OUTPUT  (feedback)
    if level > noise_floor:
        gain_db += k * (target - level)      # nudge slowly toward target
        clamp gain_db to ±max_gain
    output y
```

## Reference implementation (Python)

```python
import math

def agc(x, sr, target_db=-20.0, time_ms=1000.0,
        max_gain_db=24.0, floor_db=-60.0):
    """Feedback automatic gain control — pure standard library, no dependencies.

    Slowly drives the *output* level toward target_db by adjusting one smoothed
    gain. The slow time constant is what makes it transparent: it corrects
    long-term level drift while leaving short-term dynamics alone.

    x:  list of mono samples in [-1, 1]
    sr: sample rate (Hz)
    Returns a new list of samples.
    """
    coeff = math.exp(-1.0 / (sr * time_ms / 1000.0))   # one-pole time constant
    eps = 1e-9
    gain_db = 0.0      # the loop's state: current gain, in dB
    env = 0.0          # smoothed |output| envelope
    out = []
    for s in x:
        g = 10.0 ** (gain_db / 20.0)                    # dB -> linear
        y = s * g                                       # apply the gain
        env = coeff * env + (1.0 - coeff) * abs(y)      # measure the OUTPUT
        level_db = 20.0 * math.log10(env + eps)
        if level_db > floor_db:                         # don't chase silence
            error_db = target_db - level_db
            gain_db += (1.0 - coeff) * error_db         # slow integrator
            gain_db = max(-max_gain_db, min(max_gain_db, gain_db))
        out.append(y)
    return out
```

!!! warning "Pitfalls"
    - Pumping and breathing. Without the noise-floor guard, the gain rises during pauses
      and amplifies hiss; when sound returns it lurches back down. Slow time constants and
      a noise floor prevent this.
    - Too fast is not AGC. Shorten the time constant and the loop stops being transparent;
      it becomes a leveler or limiter and changes the subjective sound.
    - No peak protection. AGC boost can push transients into clipping; a downstream
      [limiter](limiter.md) is the standard guard.
    - Feedback instability. Too much loop gain makes the control hunt or oscillate around
      the target instead of settling.

## Related effects

- [Measuring sound](conventions.md) and [Envelopes](envelopes.md): the level detector and
  one-pole follower AGC is built from.
- [Compression](compression.md): faster, usually feed-forward; reshapes short-term
  dynamics.
- [Limiting](limiter.md): AGC's flattening with a compressor's speed.

## Learn more

- J. M. Woodgate, ISCVE Engineering Note 27.1, "Automatic gain control, limiting and
  compression" (anchored to IEC 60268-8) — the clearest taxonomy of the three.
- WebRTC AGC2 — a modern, digital, open-source AGC in the browser audio pipeline. (Check
  its license before reusing code.)
- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley — frames AGC,
  compression, and expansion as one family.
- [Automatic gain control — Wikipedia](https://en.wikipedia.org/wiki/Automatic_gain_control) — for the closed-loop definition. Heavily analog/radio; this book uses the digital realization.
