# Automatic Gain Control

> **Automatic Gain Control (AGC)** automatically holds a signal's level near a chosen target,
> correcting slow drift in loudness — *transparently*, without reshaping the moment-to-moment
> dynamics.

*Chapter 5 — time-domain level effects. The slow, transparent member of the family; builds
on [Measuring sound](conventions.md) and the envelope follower of
[Chapter 4](waveforms.md).*

---

## Intuition — what & why

Picture a sound engineer with a slow, patient hand on the volume fader during a panel
discussion: one guest leans in and booms, another sits back and murmurs. The engineer rides
the fader over *seconds* to keep everyone at a comfortable, even loudness — but doesn't yank it
on every syllable. **AGC is that slow hand, automated.**

You'd use it to even out long-term level differences: a lavalier mic on a presenter who turns
their head, a recording where the source drifts louder and quieter over minutes, a voice-chat
stream where every participant should arrive at the listener at the same level.

!!! note "Is AGC an effect, a technique, or a goal?"
    Mostly a **goal**, realized as a **control technique** — and only loosely "an effect."
    Unlike a compressor, there is no single canonical "AGC algorithm"; the name describes an
    *objective* ("hold the output near a target") rather than one specific transfer function.
    In practice it's built as a **slow feedback loop** from familiar primitives — a level
    detector ([Chapter 2](conventions.md)) plus a one-pole follower
    ([Chapter 4](waveforms.md)) — wired to seek a target instead of applying a fixed curve.

## Key parameters

| Parameter | What it controls |
|---|---|
| **Target level** | The level (dBFS) the loop drives the output toward. |
| **Time constant** | How fast it corrects. Slow (≈1 s or more) keeps it *transparent*; speed it up and it stops being AGC and becomes a leveler/limiter. |
| **Max gain** | A ceiling on how much boost it may apply — stops it over-amplifying quiet passages and noise. |
| **Noise floor** | A level below which it stops adapting, so it doesn't "pump up" silence. |

## How it works

AGC is a **closed feedback loop**. Each sample:

1. **Apply** the current gain to the input → output sample.
2. **Measure the output** level: smooth `|output|` into an envelope and convert to dBFS (this
   is the *feedback* — it watches its own output, not the input).
3. **Compare to target:** `error = target − measured_level`.
4. **Nudge the gain** slowly toward closing that error (a slow integrator), clamped to the max
   gain, and *paused* when the signal is below the noise floor.

Because the loop is **slow**, it flattens long-term level drift while leaving short-term
dynamics — the punch of individual words or notes — essentially untouched.

### Where AGC sits among its cousins

AGC, limiting, and compression are the same level-control machinery at different settings.
Following Woodgate (ISCVE Engineering Note 27.1, anchored to IEC 60268-8), they separate on two
axes — how hard they hold the output flat, and how fast they react:

| | Output held ~constant | Output less-than-proportional |
|---|---|---|
| **Slow release (≈1 s+)** | **AGC** — *transparent* | — |
| **Fast release (~ms)** | **Limiting** — *audible* | **Compression** — *audible* |

The crisp dividing line: done right, **AGC doesn't change the subjective quality** of the
program — it's corrective. Compression and limiting deliberately *do* — they're creative.
See [Compression](compression.md) for the fast, dynamics-reshaping cousin.

One consequence worth remembering: on a steady-state transfer curve, AGC and a limiter draw
the *same* flattened line. What separates them — release time — only shows in the time domain.
(The [Visualizations](visualizations.md) appendix has an interactive figure of exactly this.)

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
    - **Pumping / breathing:** without the noise-floor guard, the gain ramps up during pauses
      and amplifies hiss; when sound returns it lurches back down. Slow time constants + a noise
      floor tame this.
    - **Too fast = not AGC.** Shorten the time constant and it stops being transparent — it
      becomes a leveler or limiter and starts changing the subjective sound.
    - **No peak protection.** AGC boosts can push transients into clipping; it does *not* replace
      a limiter downstream.
    - **Feedback instability.** Too aggressive a loop gain makes it hunt or oscillate around the
      target instead of settling.

## Related effects

- **[Measuring sound](conventions.md)** and **[Waveforms & envelopes](waveforms.md)** — the
  level detector and one-pole follower AGC is built from.
- **[Compression](compression.md)** — faster, feed-forward, reshapes short-term dynamics.
- **[Limiting](limiter.md)** — AGC's flattening with a compressor's speed; the bridge between the chapters.

## Learn more

- J. M. Woodgate, **ISCVE Engineering Note 27.1 — "Automatic gain control, limiting and compression"** (anchored to **IEC 60268-8**) — the clearest taxonomy of the three.
- **WebRTC AGC2** — a modern, digital, open-source AGC that runs in the browser audio pipeline. (Check its license before reusing code.)
- Udo Zölzer (ed.), **DAFX: Digital Audio Effects**, 2nd ed., Wiley — frames AGC/compression/expansion as one family.
- [Automatic gain control — Wikipedia](https://en.wikipedia.org/wiki/Automatic_gain_control) — for the closed-loop definition (note: heavily analog/radio; we use the *digital* realization).
