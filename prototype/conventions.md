# Conventions

> The shared vocabulary the rest of this cookbook leans on: how we represent audio, how we
> measure level in **dBFS**, how we convert between linear and decibel gain, and how an
> effect *follows* a signal's level over time. Every later chapter assumes these.

*Chapter 1 — Conventions & AGC. Next up: [Automatic Gain Control](agc.md).*

---

## Audio as samples

Digital audio is just a list of numbers. We take the sound pressure level many thousands of
times per second (the **sample rate**, `sr`, e.g. 44 100 or 48 000 Hz) and store each
measurement as one **sample**.

Throughout this cookbook a mono signal is a plain Python list of floats in the range
**`[-1.0, 1.0]`**:

- `0.0` is silence,
- `+1.0` and `-1.0` are the largest values the format can represent — **full scale**,
- anything beyond `±1.0` would **clip** (distort) on playback.

```python
# One second of a 440 Hz sine at half amplitude, 48 kHz.
import math

sr = 48_000
signal = [0.5 * math.sin(2 * math.pi * 440 * n / sr) for n in range(sr)]
```

!!! note "Why `[-1, 1]`?"
    It is the natural, format-independent range for floating-point audio: the math stays the
    same whether the file is later rendered to 16-bit, 24-bit, or anything else. We never
    work in raw integer sample values here.

## Measuring level: decibels and dBFS

Loudness spans a huge range, so we measure it **logarithmically**, in **decibels (dB)**. For
an amplitude `a` (a linear value like a sample magnitude), the level is:

```
level_dB = 20 · log10(a)
```

Because our samples live in `[-1, 1]`, the reference point is **full scale**, and the unit is
**dBFS** — *decibels relative to full scale*:

- amplitude `1.0` → **0 dBFS** (the loudest representable level),
- everything quieter is **negative** (e.g. `0.5` → −6 dBFS),
- `0.0` → −∞ dBFS (silence).

| Linear amplitude | dBFS |
|---|---|
| 1.0 | 0 |
| 0.5 | −6.0 |
| 0.25 | −12.0 |
| 0.1 | −20.0 |
| 0.01 | −40.0 |
| 0.001 | −60.0 |

Two rules of thumb fall out of the math and are worth memorising: **halving** the amplitude is
about **−6 dB**, and dividing by **ten** is exactly **−20 dB**.

```python
import math

def db_from_amplitude(a):
    """Linear amplitude -> dBFS. Silence maps to -inf."""
    a = abs(a)
    return 20.0 * math.log10(a) if a > 0.0 else float("-inf")

def amplitude_from_db(db):
    """dBFS -> linear amplitude."""
    return 10.0 ** (db / 20.0)
```

!!! note "dBFS vs. dBA, dB SPL, …"
    Other decibel scales exist. **dB SPL** measures real-world acoustic pressure, and
    **dBA** applies [A-weighting](https://en.wikipedia.org/wiki/A-weighting) — a frequency
    curve that approximates how loud humans *perceive* a sound. Those are about acoustics and
    perception; we are inside the computer working on samples, so **dBFS is our unit
    everywhere**. We mention dBA only as related context.

## Gain: linear and in dB

**Gain** is just multiplication: to make a signal louder or quieter you multiply every sample
by a constant. A gain of `1.0` changes nothing; `0.5` is half amplitude (−6 dB); `2.0` is
double (+6 dB).

We *talk* about gain in dB but *apply* it linearly, so converting between the two is constant
work in every effect:

```python
def apply_gain_db(signal, gain_db):
    """Return a new signal scaled by gain_db (in dB)."""
    g = amplitude_from_db(gain_db)        # dB -> linear, once
    return [s * g for s in signal]
```

!!! warning "Keep dB and linear straight"
    Decibels **add**; linear gains **multiply**. Two stages of +6 dB give +12 dB, which is
    ×4 in linear terms — not ×2 + ×2. Mixing the two domains is the most common beginner bug.

## Detecting level: peak vs. RMS

An effect that reacts to "how loud is it right now" first needs a number for the current
level. Two common detectors:

- **Peak** — the largest magnitude in a window. Fast, catches transients, good for catching
  clipping.
- **RMS** (root-mean-square) — the energy average over a window. Smoother, and closer to
  perceived loudness.

```python
def peak(block):
    """Peak amplitude of a block of samples."""
    return max((abs(s) for s in block), default=0.0)

def rms(block):
    """Root-mean-square amplitude of a block of samples."""
    if not block:
        return 0.0
    return math.sqrt(sum(s * s for s in block) / len(block))
```

For a sine wave, RMS sits about **3 dB below** the peak — so the choice of detector shifts
your measured level. Most level effects in this book detect on one of these and then report
the result in dBFS via `db_from_amplitude`.

## Following level over time: attack & release

Effects rarely react instantly — that would sound harsh and distort. Instead they **smooth**
their response with time constants:

- **Attack** — how quickly the effect responds when the level *rises*.
- **Release** — how quickly it relaxes when the level *falls*.

The standard tool is a **one-pole smoother** (a.k.a. exponential follower). A coefficient
derived from a time-in-milliseconds controls how sluggish it is:

```python
def smoothing_coeff(time_ms, sr):
    """One-pole coefficient for a given time constant at sample rate sr."""
    return math.exp(-1.0 / (sr * time_ms / 1000.0))

def follow(signal, attack_ms, release_ms, sr):
    """Trace a signal's envelope: fast up (attack), slow down (release)."""
    atk = smoothing_coeff(attack_ms, sr)
    rel = smoothing_coeff(release_ms, sr)
    env = 0.0
    out = []
    for s in signal:
        target = abs(s)
        coeff = atk if target > env else rel   # attack when rising, release when falling
        env = coeff * env + (1.0 - coeff) * target
        out.append(env)
    return out
```

This `follow` pattern — measure, then smooth toward the measurement — is the backbone of
[AGC](agc.md) and every effect in the [Companding](compression.md) chapter. Each one differs
mainly in *what* it does with the smoothed level once it has it.

## Visualization

!!! note "Interactive visual"
    *Placeholder — a browser-based plot of amplitude, dBFS, and an envelope follower slots in
    here.* Static now; client-side interactive later (see `visualization/`).

## Pitfalls

!!! warning "Common mistakes"
    - **`log10(0)` is undefined.** Guard silence before taking a logarithm (we return −∞).
    - **dB ≠ linear.** Convert deliberately; never add a dB value to a sample.
    - **Detector choice matters.** Peak and RMS of the same signal differ by several dB —
      state which one a measurement uses.
    - **Sample rate is part of every time constant.** The same `attack_ms` gives a different
      coefficient at 44.1 kHz vs. 48 kHz; always pass `sr` through.

## Learn more

- [dBFS](https://en.wikipedia.org/wiki/DBFS) and [Decibel](https://en.wikipedia.org/wiki/Decibel) — Wikipedia, for the measurement basics.
- [Root mean square](https://en.wikipedia.org/wiki/Root_mean_square) — Wikipedia.
- Udo Zölzer (ed.), **DAFX: Digital Audio Effects**, 2nd ed., Wiley, 2011 — the standard reference for this whole cookbook.
- Julius O. Smith III, **Introduction to Digital Filters**, CCRMA (free online) — for one-pole smoothers / exponential followers.

> *Citations above are starting points and should be verified before publication, per the
> project's attribution policy (DESIGN.md §7).*
