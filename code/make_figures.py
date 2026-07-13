"""Generate the book's static figures as SVG.

Standard library only. The time-domain figures are produced by running signals
through the book's own reference implementation (compressor.py), so every curve
shown is the output of code the reader can run.

Run from the repo root:  python3 code/make_figures.py
Output:                  prototype/img/*.svg  (served by MkDocs, committed to git)

Figure conventions (from the feedback log, research/confusions.md #12-14):
  1. Legend swatches carry the same stroke and dash as their lines.
  2. An effect's inactive stretches (output = input) are drawn faint, not bold.
  3. Every reference level an effect owns is drawn and named. Reference levels
     are dashed purple across all figures.

Colors are mid-tone so the transparent-background SVGs read on both the light
and dark site themes.
"""

import math
import os

from compressor import compress, db_from_amplitude

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..",
                                         "prototype", "img"))

# Mid-tone palette, legible on light and dark backgrounds.
GRAY = "#888780"       # axes text, unity, input traces
GRID = "#888780"       # gridlines (drawn at low opacity)
GREEN = "#1baf7a"      # 2:1
BLUE = "#378add"       # 4:1, outputs
RED = "#e05252"        # infinite ratio / limiter
AMBER = "#d98a00"      # gain reduction
PURPLE = "#7f77dd"     # reference levels (threshold, target)

FONT = 'font-family="system-ui, sans-serif"'


# --------------------------------------------------------------------------
# Minimal SVG helpers
# --------------------------------------------------------------------------

class Plot:
    """A single x/y plot with dB-style axes, rendered to an SVG string."""

    def __init__(self, width, height, x_range, y_range, title, desc):
        self.w, self.h = width, height
        self.x_min, self.x_max = x_range
        self.y_min, self.y_max = y_range
        self.x0, self.x1 = 46, width - 14
        self.y0, self.y1 = height - 34, 14
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{title}">',
            f'<title>{title}</title>',
            f'<desc>{desc}</desc>',
        ]

    def sx(self, v):
        return self.x0 + (v - self.x_min) / (self.x_max - self.x_min) * (self.x1 - self.x0)

    def sy(self, v):
        return self.y0 + (v - self.y_min) / (self.y_max - self.y_min) * (self.y1 - self.y0)

    def grid(self, x_step, y_step, x_label, y_label, x_tick_fmt=str,
             y_tick_fmt=lambda v: str(int(v))):
        p = self.parts
        p.append(f'<g stroke="{GRID}" stroke-opacity="0.25" stroke-width="1">')
        v = self.x_min
        while v <= self.x_max + 1e-9:
            x = self.sx(v)
            p.append(f'<line x1="{x:.1f}" y1="{self.y0}" x2="{x:.1f}" y2="{self.y1}"/>')
            v += x_step
        v = self.y_min
        while v <= self.y_max + 1e-9:
            y = self.sy(v)
            p.append(f'<line x1="{self.x0}" y1="{y:.1f}" x2="{self.x1}" y2="{y:.1f}"/>')
            v += y_step
        p.append('</g>')
        p.append(f'<g fill="{GRAY}" font-size="11" {FONT}>')
        v = self.x_min
        while v <= self.x_max + 1e-9:
            p.append(f'<text x="{self.sx(v):.1f}" y="{self.y0 + 16}" '
                     f'text-anchor="middle">{x_tick_fmt(v)}</text>')
            v += x_step
        v = self.y_min
        while v <= self.y_max + 1e-9:
            p.append(f'<text x="{self.x0 - 6}" y="{self.sy(v) + 3:.1f}" '
                     f'text-anchor="end">{y_tick_fmt(v)}</text>')
            v += y_step
        p.append(f'<text x="{(self.x0 + self.x1) / 2:.1f}" y="{self.y0 + 30}" '
                 f'text-anchor="middle">{x_label}</text>')
        p.append(f'<text x="13" y="{(self.y0 + self.y1) / 2:.1f}" text-anchor="middle" '
                 f'transform="rotate(-90 13 {(self.y0 + self.y1) / 2:.1f})">{y_label}</text>')
        p.append('</g>')

    def _pts(self, xs, ys):
        return " ".join(f"{self.sx(x):.1f},{self.sy(y):.1f}" for x, y in zip(xs, ys))

    def line(self, xs, ys, color, width=2.2, dash=None, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' stroke-opacity="{opacity}"' if opacity < 1.0 else ""
        self.parts.append(f'<polyline points="{self._pts(xs, ys)}" fill="none" '
                          f'stroke="{color}" stroke-width="{width}"{d}{o}/>')

    def segments(self, xs, ys, active, color, width=2.6):
        """Polyline drawn only where active[i] is true (convention 2: bold = acting)."""
        run_x, run_y = [], []
        for x, y, a in zip(xs, ys, active):
            if a:
                run_x.append(x); run_y.append(y)
            elif run_x:
                self.line(run_x, run_y, color, width)
                run_x, run_y = [], []
        if run_x:
            self.line(run_x, run_y, color, width)

    def ref_level(self, y_value, label):
        """Convention 3: a named reference level, dashed purple."""
        y = self.sy(y_value)
        self.parts.append(f'<line x1="{self.x0}" y1="{y:.1f}" x2="{self.x1}" y2="{y:.1f}" '
                          f'stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        self.parts.append(f'<text x="{self.x1 - 4}" y="{y - 5:.1f}" text-anchor="end" '
                          f'fill="{PURPLE}" font-size="10" {FONT}>{label}</text>')

    def ref_vertical(self, x_value, label):
        x = self.sx(x_value)
        self.parts.append(f'<line x1="{x:.1f}" y1="{self.y0}" x2="{x:.1f}" y2="{self.y1}" '
                          f'stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        self.parts.append(f'<text x="{x + 5:.1f}" y="{self.y1 + 10}" text-anchor="start" '
                          f'fill="{PURPLE}" font-size="10" {FONT}>{label}</text>')

    def legend(self, entries, x, y):
        """entries: (label, color, dash, width). Swatches mirror the lines
        exactly (convention 1)."""
        p = self.parts
        for i, (label, color, dash, width) in enumerate(entries):
            yy = y + i * 15
            d = f' stroke-dasharray="{dash}"' if dash else ""
            p.append(f'<line x1="{x}" y1="{yy}" x2="{x + 20}" y2="{yy}" '
                     f'stroke="{color}" stroke-width="{width}"{d}/>')
            p.append(f'<text x="{x + 26}" y="{yy + 3.5}" fill="{GRAY}" '
                     f'font-size="11" {FONT}>{label}</text>')

    def save(self, name):
        self.parts.append('</svg>')
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.parts) + "\n")
        print(f"wrote {path}")


# --------------------------------------------------------------------------
# Signal helpers
# --------------------------------------------------------------------------

def burst_tone(sr, freq, sections):
    """Sine tone whose amplitude steps through (duration_s, amplitude) sections."""
    out = []
    n = 0
    for dur, amp in sections:
        for _ in range(int(dur * sr)):
            out.append(amp * math.sin(2 * math.pi * freq * n / sr))
            n += 1
    return out


def block_peak_db(x, block):
    """Per-block peak envelope in dBFS (peak), one point per block."""
    env = []
    for i in range(0, len(x) - block + 1, block):
        peak = max(abs(s) for s in x[i:i + block])
        env.append(db_from_amplitude(peak) if peak > 0 else -120.0)
    return env


# --------------------------------------------------------------------------
# Figure 1: compression static transfer curves
# --------------------------------------------------------------------------

def fig_compression_transfer():
    T = -20.0
    plot = Plot(520, 360, (-60, 0), (-60, 0),
                "Compression transfer curves",
                "Steady-state output level versus input level at a -20 dBFS "
                "threshold, hard knee. Below the threshold all ratios follow the "
                "unity line; above it, 2:1 and 4:1 reduce the slope and an "
                "infinite ratio holds the output flat at the threshold.")
    plot.grid(10, 10, "input dBFS (peak)", "output dBFS (peak)")
    plot.ref_vertical(T, "threshold")

    xs = [x * 0.5 for x in range(-120, 1)]

    def curve(ratio):
        return [x if x <= T else T + (x - T) / ratio for x in xs]

    plot.line(xs, xs, GRAY, 1.6, dash="5 4")                    # unity
    plot.line(xs, curve(2), GREEN)
    plot.line(xs, curve(4), BLUE)
    plot.line(xs, curve(math.inf), RED, 2.6)
    plot.legend([
        ("unity (no processing)", GRAY, "5 4", 1.6),
        ("2:1", GREEN, None, 2.2),
        ("4:1", BLUE, None, 2.2),
        ("∞:1 (limiter)", RED, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 18)
    plot.save("compression_transfer.svg")


# --------------------------------------------------------------------------
# Figure 2: compression in the time domain (gain reduction trace)
# --------------------------------------------------------------------------

def fig_compression_gain_reduction():
    sr, block = 8000, 40                       # 5 ms envelope blocks
    T = -20.0
    quiet = 10 ** (-24.0 / 20.0)               # -24 dBFS
    loud = 10 ** (-6.0 / 20.0)                 # -6 dBFS
    x = burst_tone(sr, 220.0, [(0.25, quiet), (0.25, loud), (0.25, quiet)])

    y = compress(x, sr, threshold_db=T, ratio=4.0, knee="hard",
                 attack_ms=5.0, release_ms=50.0)

    in_env = block_peak_db(x, block)
    out_env = block_peak_db(y, block)
    gain = [o - i for i, o in zip(in_env, out_env)]
    t = [i * block / sr for i in range(len(in_env))]
    active = [g < -0.1 for g in gain]

    plot = Plot(520, 360, (0, 0.75), (-40, 0),
                "Compression gain reduction over time",
                "A quiet-loud-quiet tone through the book's compressor at 4:1 "
                "with a -20 dBFS threshold. The gain reduction trace dives when "
                "the loud section starts (5 ms attack) and recovers after it "
                "ends (50 ms release). The output is drawn bold only while gain "
                "reduction is active; elsewhere it equals the input.")
    plot.grid(0.25, 10, "time (s)", "level dBFS (peak)",
              x_tick_fmt=lambda v: f"{v:.2f}")
    plot.ref_level(T, "threshold (−20 dBFS)")

    plot.line(t, in_env, GRAY, 2.0, dash="4 3")                 # input envelope
    plot.line(t, out_env, BLUE, 1.5, opacity=0.35)              # output, faint
    plot.segments(t, out_env, active, BLUE, 2.6)                # output, acting
    plot.line(t, gain, AMBER, 2.2)                              # gain reduction
    plot.legend([
        ("input level", GRAY, "4 3", 2.0),
        ("output — bold where compressing", BLUE, None, 2.6),
        ("gain reduction (dB)", AMBER, None, 2.2),
        ("threshold", PURPLE, "5 4", 1.5),
    ], x=plot.x0 + 14, y=plot.sy(-27))
    plot.save("compression_gain_reduction.svg")


# --------------------------------------------------------------------------
# Figure 3: limiter static transfer curve
# --------------------------------------------------------------------------

def fig_limiter_transfer():
    C = -10.0
    plot = Plot(520, 360, (-60, 0), (-60, 0),
                "Limiter transfer curve",
                "Steady-state output versus input. Below the -10 dBFS ceiling "
                "the limiter follows the unity line; above it the output is "
                "held flat at the ceiling. A 4:1 compressor at the same corner "
                "is shown for contrast: it leans where the limiter walls.")
    plot.grid(10, 10, "input dBFS (peak)", "output dBFS (peak)")
    plot.ref_level(C, "ceiling (−10 dBFS)")

    xs = [x * 0.5 for x in range(-120, 1)]
    plot.line(xs, xs, GRAY, 1.6, dash="5 4")                            # unity
    plot.line(xs, [x if x <= C else C + (x - C) / 4 for x in xs], BLUE)  # 4:1
    plot.line(xs, [min(x, C) for x in xs], RED, 2.6)                    # wall
    plot.legend([
        ("unity (no processing)", GRAY, "5 4", 1.6),
        ("compression 4:1, same threshold", BLUE, None, 2.2),
        ("limiter (∞:1)", RED, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("limiter_transfer.svg")


# --------------------------------------------------------------------------
# Figure 4: limiter in time — overshoot without lookahead vs true lookahead
# --------------------------------------------------------------------------

def fig_limiter_lookahead():
    sr, block = 8000, 16                       # 2 ms envelope blocks
    C = -10.0
    quiet = 10 ** (-25.0 / 20.0)
    loud = 10 ** (-4.0 / 20.0)
    x = burst_tone(sr, 500.0, [(0.1, quiet), (0.1, loud), (0.1, quiet)])

    kw = dict(threshold_db=C, ratio=math.inf, knee="hard",
              attack_ms=2.0, release_ms=40.0)
    y_none = compress(x, sr, lookahead="none", **kw)
    y_true = compress(x, sr, lookahead="true", lookahead_ms=6.0, **kw)

    t = [i * block / sr for i in range(len(x) // block)]
    in_env = block_peak_db(x, block)
    envs = {}
    for name, y in (("none", y_none), ("true", y_true)):
        env = block_peak_db(y, block)
        envs[name] = (env, [o - i < -0.1 for i, o in zip(in_env, env)])

    plot = Plot(520, 360, (0, 0.3), (-30, 0),
                "Limiter overshoot with and without lookahead",
                "A quiet-loud-quiet tone through the book's limiter. Without "
                "lookahead the output overshoots the ceiling while the 2 ms "
                "attack catches up. With 6 ms of true lookahead the gain is "
                "pre-armed and the output never crosses the ceiling; the "
                "lookahead output is delayed by the lookahead time.")
    plot.grid(0.1, 10, "time (s)", "level dBFS (peak)",
              x_tick_fmt=lambda v: f"{v:.1f}")
    plot.ref_level(C, "ceiling (−10 dBFS)")

    plot.line(t, in_env, GRAY, 2.0, dash="4 3")
    for name, color in (("none", AMBER), ("true", BLUE)):
        env, active = envs[name]
        plot.line(t, env, color, 1.5, opacity=0.35)
        plot.segments(t, env, active, color, 2.6)
    plot.legend([
        ("input level", GRAY, "4 3", 2.0),
        ("no lookahead — overshoots", AMBER, None, 2.6),
        ("true lookahead 6 ms — delayed, no overshoot", BLUE, None, 2.6),
        ("ceiling", PURPLE, "5 4", 1.5),
    ], x=plot.x0 + 14, y=plot.sy(-21))
    plot.save("limiter_lookahead.svg")


# --------------------------------------------------------------------------
# Figure 5: expander static transfer curve
# --------------------------------------------------------------------------

def fig_expander_transfer():
    T = -35.0
    plot = Plot(520, 360, (-60, 0), (-60, 0),
                "Expander transfer curves",
                "Steady-state output versus input. Above the -35 dBFS "
                "threshold the expander follows the unity line; below it the "
                "output drops faster than the input, 2:1 gently and 4:1 "
                "steeply enough to act as a gate.")
    plot.grid(10, 10, "input dBFS (peak)", "output dBFS (peak)")
    plot.ref_vertical(T, "threshold")

    xs = [x * 0.5 for x in range(-120, 1)]

    def curve(ratio):
        return [x if x >= T else T + (x - T) * ratio for x in xs]

    plot.line(xs, xs, GRAY, 1.6, dash="5 4")
    plot.line(xs, curve(2), GREEN)
    plot.line(xs, curve(4), RED, 2.6)
    plot.legend([
        ("unity (no processing)", GRAY, "5 4", 1.6),
        ("2:1 expansion", GREEN, None, 2.2),
        ("4:1 — a gate, nearly", RED, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("expander_transfer.svg")


# --------------------------------------------------------------------------
# Figure 6: expander/gate in time
# --------------------------------------------------------------------------

def _expand(x, sr, threshold_db, ratio, range_db, attack_ms, release_ms):
    """Mirrors the reference implementation on the Expanding page."""
    atk = math.exp(-1.0 / (sr * attack_ms / 1000.0))
    rel = math.exp(-1.0 / (sr * release_ms / 1000.0))
    eps = 1e-9
    y = []
    env_db = 0.0
    for sample in x:
        level_db = 20.0 * math.log10(abs(sample) + eps)
        under = threshold_db - level_db
        target = -under * (ratio - 1.0) if under > 0.0 else 0.0
        target = max(target, range_db)
        coeff = atk if target > env_db else rel
        env_db = coeff * env_db + (1.0 - coeff) * target
        y.append(sample * 10.0 ** (env_db / 20.0))
    return y


def fig_expander_gate():
    sr, block = 8000, 40                       # 5 ms envelope blocks
    T = -35.0
    bleed = 10 ** (-45.0 / 20.0)
    voice = 10 ** (-10.0 / 20.0)
    x = burst_tone(sr, 500.0, [(0.15, bleed), (0.12, voice), (0.2, bleed),
                               (0.12, voice), (0.16, bleed)])
    y = _expand(x, sr, threshold_db=T, ratio=3.0, range_db=-25.0,
                attack_ms=5.0, release_ms=100.0)

    in_env = block_peak_db(x, block)
    out_env = block_peak_db(y, block)
    active = [o - i < -0.1 for i, o in zip(in_env, out_env)]
    t = [i * block / sr for i in range(len(in_env))]

    plot = Plot(520, 360, (0, 0.75), (-80, 0),
                "Expander closing on the quiet parts",
                "Two loud bursts over a -45 dBFS bleed floor, through the "
                "book's expander at 3:1 below a -35 dBFS threshold. Between "
                "bursts the expander pushes the bleed down by its full range; "
                "it opens quickly when a burst arrives (5 ms attack) and "
                "closes slowly after it ends (100 ms release). The output is "
                "bold only while the expander is attenuating.")
    plot.grid(0.25, 20, "time (s)", "level dBFS (peak)",
              x_tick_fmt=lambda v: f"{v:.2f}")
    plot.ref_level(T, "threshold (−35 dBFS)")

    plot.line(t, in_env, GRAY, 2.0, dash="4 3")
    plot.line(t, out_env, BLUE, 1.5, opacity=0.35)
    plot.segments(t, out_env, active, BLUE, 2.6)
    plot.legend([
        ("input level", GRAY, "4 3", 2.0),
        ("output — bold where attenuating", BLUE, None, 2.6),
        ("threshold", PURPLE, "5 4", 1.5),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("expander_gate.svg")


# --------------------------------------------------------------------------
# Figure 7: the envelope follower (Conventions)
# --------------------------------------------------------------------------

def fig_envelope_follower():
    sr = 8000
    x = burst_tone(sr, 220.0, [(0.08, 0.1), (0.1, 0.5), (0.17, 0.1)])

    # Mirrors follow() on the Conventions page.
    atk = math.exp(-1.0 / (sr * 5.0 / 1000.0))     # 5 ms attack
    rel = math.exp(-1.0 / (sr * 50.0 / 1000.0))    # 50 ms release
    env, envs = 0.0, []
    for s in x:
        target = abs(s)
        coeff = atk if target > env else rel
        env = coeff * env + (1.0 - coeff) * target
        envs.append(env)

    step = 2                                       # plot every 2nd sample
    t = [i / sr for i in range(0, len(x), step)]
    rect = [abs(x[i]) for i in range(0, len(x), step)]
    env_pts = [envs[i] for i in range(0, len(x), step)]

    plot = Plot(520, 360, (0, 0.35), (0, 0.6),
                "An envelope follower tracing a burst",
                "The rectified samples of a quiet-loud-quiet tone, and the "
                "one-pole envelope that follows them: it rises with the burst "
                "in about 5 ms (attack) and decays after it in about 50 ms "
                "(release). Linear amplitude, not dB.")
    plot.grid(0.1, 0.1, "time (s)", "amplitude (linear)",
              x_tick_fmt=lambda v: f"{v:.1f}", y_tick_fmt=lambda v: f"{v:.1f}")

    plot.line(t, rect, GRAY, 1.0, opacity=0.5)
    plot.line(t, env_pts, BLUE, 2.4)
    plot.legend([
        ("|x| — rectified samples", GRAY, None, 1.0),
        ("envelope — 5 ms attack, 50 ms release", BLUE, None, 2.4),
    ], x=plot.x0 + 190, y=plot.y1 + 16)
    plot.save("envelope_follower.svg")


# --------------------------------------------------------------------------
# Figures 8-11: single-sample transfer curves (Chapter 3)
#
# These are linear-amplitude plots (input sample vs. output sample, both in
# [-1, 1]), not dB: a single sample has no level. Unity keeps the same dashed
# gray as everywhere else in the book.
# --------------------------------------------------------------------------

def _linear_plot(title, desc):
    plot = Plot(520, 360, (-1.0, 1.0), (-1.0, 1.0), title, desc)
    plot.grid(0.5, 0.5, "input sample", "output sample",
              x_tick_fmt=lambda v: f"{v:.1f}", y_tick_fmt=lambda v: f"{v:.1f}")
    xs = [i / 200.0 for i in range(-200, 201)]
    plot.line(xs, xs, GRAY, 1.6, dash="5 4")          # unity
    return plot, xs


def fig_volume_transfer():
    plot, xs = _linear_plot(
        "Volume transfer curves",
        "Input sample versus output sample. A gain of 0.5 is a shallower "
        "line through the origin; a gain of 2 is steeper and runs into the "
        "±1.0 limits, where it clips.")
    plot.line(xs, [0.5 * x for x in xs], GREEN)
    plot.line(xs, [max(-1.0, min(1.0, 2.0 * x)) for x in xs], RED, 2.6)
    plot.legend([
        ("unity (gain 1)", GRAY, "5 4", 1.6),
        ("gain 0.5 (−6 dB)", GREEN, None, 2.2),
        ("gain 2 (+6 dB) — clips at full scale", RED, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("volume_transfer.svg")


def fig_distortion_transfer():
    plot, xs = _linear_plot(
        "Distortion transfer curves",
        "Hard clipping flattens everything past the limit into a plateau "
        "with sharp corners; tanh soft clipping bends toward the same "
        "limits gradually. Both drawn at a drive of 3.")
    plot.line(xs, [max(-1.0, min(1.0, 3.0 * x)) for x in xs], RED, 2.6)
    plot.line(xs, [math.tanh(3.0 * x) for x in xs], BLUE, 2.6)
    plot.legend([
        ("unity (no distortion)", GRAY, "5 4", 1.6),
        ("hard clip, drive 3", RED, None, 2.6),
        ("soft clip (tanh), drive 3", BLUE, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("distortion_transfer.svg")


def fig_bitcrush_transfer():
    levels = 4                                        # 3 bits: 4 steps per side
    plot, xs = _linear_plot(
        "Bit crush transfer curve",
        "Three-bit quantization: every input sample is rounded to the "
        "nearest of a few output levels, turning the unity line into a "
        "staircase. The gap between staircase and unity is the "
        "quantization error.")
    plot.line(xs, [round(x * levels) / levels for x in xs], BLUE, 2.6)
    plot.legend([
        ("unity (full precision)", GRAY, "5 4", 1.6),
        ("3-bit quantization", BLUE, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("bitcrush_transfer.svg")


def fig_mulaw_transfer():
    mu = 255.0
    ln1mu = math.log(1.0 + mu)

    def comp(x):
        return math.copysign(math.log(1.0 + mu * abs(x)) / ln1mu, x)

    def expand(y):
        return math.copysign(((1.0 + mu) ** abs(y) - 1.0) / mu, y)

    plot, xs = _linear_plot(
        "Mu-law transfer curves",
        "The mu-law compression curve is steep near zero, spending most of "
        "its output range on quiet samples; the expansion curve is its "
        "exact inverse. Mu is 255, the G.711 telephony value.")
    plot.line(xs, [comp(x) for x in xs], BLUE, 2.6)
    plot.line(xs, [expand(x) for x in xs], GREEN, 2.6)
    plot.legend([
        ("unity", GRAY, "5 4", 1.6),
        ("compress (before quantizing)", BLUE, None, 2.6),
        ("expand (after: the inverse)", GREEN, None, 2.6),
    ], x=plot.x0 + 14, y=plot.y1 + 16)
    plot.save("mulaw_transfer.svg")


if __name__ == "__main__":
    fig_compression_transfer()
    fig_compression_gain_reduction()
    fig_limiter_transfer()
    fig_limiter_lookahead()
    fig_expander_transfer()
    fig_expander_gate()
    fig_envelope_follower()
    fig_volume_transfer()
    fig_distortion_transfer()
    fig_bitcrush_transfer()
    fig_mulaw_transfer()
