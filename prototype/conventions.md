# Conventions

> The shared vocabulary the rest of this cookbook leans on: how we represent audio, how we
> measure level in **dBFS**, how we convert between linear and decibel gain, and how an
> effect *follows* a signal's level over time. Every later chapter assumes these.

*Chapter 1 — Conventions & AGC. Next up: [Automatic Gain Control](agc.md).*

---

## Audio as samples

Digital audio is just a list of numbers. We measure the signal's amplitude many thousands of
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

Signal levels span a huge range, so we measure them **logarithmically**, in **decibels (dB)**.
But getting this rigorous means being careful about three things that everyday usage blurs: a dB
always implies a *reference*, it depends on whether you're measuring *power or amplitude*, and
"dBFS" itself is only fully specified once you say *peak or RMS*.

### A decibel is a ratio — so it always needs a reference

A decibel is **dimensionless**: it's a ratio, so on its own it means nothing. It always compares
a measured value against a fixed **reference**:

```
dB = 10 · log10( measured / reference )      # (for power quantities — see below)
```

- The **numerator** is what you're measuring; the **denominator** is a fixed, agreed reference.
- With **no fixed reference**, a dB is only a *relative change* — this is how we talk about
  **gain** ("+6 dB" = ×2 amplitude). With a **standard reference**, it names an *absolute level*,
  and the reference is exactly what the suffix means: dB**FS**, dB **SPL**, ….

So **never write a bare "dB" for a level.** Write the referenced unit — it pins down both the
reference *and* the power-vs-amplitude question below.

### Power vs. amplitude — the 10 vs. the 20

The reference must match the *kind* of quantity, and that sets the multiplier:

- **Power** quantities (intensity, electrical power): `dB = 10 · log10(P / P₀)`.
- **Amplitude / field** quantities (sound pressure, voltage, **our sample values**):
  `dB = 20 · log10(A / A₀)` — the 20 appears because power ∝ amplitude².

The two are built to *agree* for the same physical change (doubling amplitude and quadrupling
power are both **+6 dB**), so the dB number itself **never tells you which you measured** — the
**unit** does:

| Unit | Measures | Reference | Quantity → factor | Domain |
|---|---|---|---|---|
| **dBFS** | sample amplitude | full scale (1.0) | amplitude → 20·log | digital, absolute |
| **dB SPL** | sound pressure | 20 µPa | amplitude → 20·log | acoustic, absolute |
| **dBV / dBu** | voltage | 1 V / 0.775 V RMS | amplitude → 20·log | electrical, absolute |
| **dBm** | electrical power | 1 mW | power → 10·log | electrical, absolute |
| **dB SIL / SWL** | sound intensity / power | 10⁻¹² W/m² · W | power → 10·log | acoustic, absolute |
| **dB** (gain) | a *change* | the other signal | match the quantity | relative |

The units audio work touches most (dBFS, dB SPL, dBV/dBu) are all **amplitude** quantities, so
**20·log** is our default throughout — but the discipline is to *know* that, not assume it.

### dBFS — our unit

We work on samples, so our reference is **full scale** (amplitude `1.0`) and our unit is **dBFS**
(decibels relative to full scale). Samples are amplitudes, so it's the 20·log form:

```
dBFS = 20 · log10( |sample| / 1.0 )
```

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

Two rules of thumb fall out of the math: **halving** the amplitude is about **−6 dB**, and
dividing by **ten** is exactly **−20 dB**.

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

### Peak vs. RMS dBFS — always say which

Even "dBFS" is under-specified: the number depends on *how* you reduce the signal to one value.
We fix **one reference (full scale = 1.0)** and always **label the detector**:

- **dBFS (peak)** — the instantaneous sample magnitude, `20·log10(|x|)`. Sample-peak can't
  exceed 0 dBFS. **This is our primary unit** — the per-sample detectors report it.
- **dBFS (RMS)** — the energy average over a window, `20·log10(rms)`, against the **same**
  1.0 reference.

For one full-scale sine those give **0 dBFS (peak)** but **−3.01 dBFS (RMS)** — and that 3 dB gap
*is* the signal's **crest factor**. Keeping a single honest reference means RMS reads exactly
what the math says.

!!! example "Worked example: the −3.01 dB of a full-scale sine"
    Take a sine with peak amplitude 1.0. There are two correct routes to its RMS level, and
    one common wrong turn.

    - **Amplitude route.** The RMS amplitude is 1/√2 ≈ 0.707. Amplitude takes the 20
      multiplier: `20 · log10(0.707)` = **−3.01 dBFS (RMS)**.
    - **Power route.** The mean power is the square of the RMS amplitude: 0.707² = 0.5.
      Power takes the 10 multiplier: `10 · log10(0.5)` = **−3.01 dB**. The two routes agree,
      as they must — the 10/20 convention exists so that they do.
    - **The wrong turn.** Pair the amplitude value with the power multiplier,
      `10 · log10(0.707)`, and you get −1.5 dB. A result at exactly half (or double) the
      expected value is the fingerprint of a 10/20 mix-up.

    The phrase "RMS power" usually sets this trap. RMS is an amplitude; its square is the
    power. Say "RMS amplitude" (0.707) or "mean power" (0.5) and the multiplier chooses
    itself.

!!! note "We do not use the AES17 RMS offset"
    Broadcast meters (AES17) *re-reference* RMS so that a full-scale **sine** reads 0 dBFS RMS —
    a fixed **+3.01 dB** offset (a full-scale square then reads +3 dBFS RMS). We deliberately
    **don't**: the offset is a magic constant that hides the crest factor. The cost is that our
    RMS numbers sit ~3 dB below what a typical DAW meter shows — if you compare to one, that's why.

!!! warning "Peak-to-peak is not a level"
    In our range the signal *spans* up to 2 (from −1 to +1), but level is never measured
    peak-to-peak. A detector that uses `max − min` reads 6 dB hot next to a true peak detector
    (20·log₁₀ 2 ≈ 6.02 dB); one of the open-source compressors we surveyed makes exactly this
    mistake. Measure the magnitude `|x|` (peak) or the RMS, never the span. A useful sanity
    check for any reading: **RMS ≤ peak ≤ 1.0**, so nothing in this system can exceed 0 dBFS.

### Level vs. loudness vs. volume

These everyday words hop between the *objective* and the *perceptual*, which is where rigor
slips. Keep them separate:

- **Level** — an *objective* signal measure, in dB (what we compute). When this book says
  "louder," it means **higher level, in dB**.
- **Loudness** — how loud a sound *seems*: a *perceptual* quantity, nonlinearly related to level.
  Crucially, **"+6 dB" is not "twice as loud."**
- **Volume** — not a measurement at all; a *control* (a gain setting).

"Double it" is really three different requests:

| "Double it" means… | dB change | amplitude | power |
|---|---|---|---|
| ×2 **amplitude** | +6 dB | ×2 | ×4 |
| ×2 **power** | +3 dB | ×1.41 | ×2 |
| ×2 **perceived loudness** | ≈ +10 dB | ×3.16 | ×10 |

!!! note "Loudness is deferred"
    Perceived loudness has its own units (phon, sone) and an engineering proxy (LUFS), all of
    which need sound-pressure levels and models of hearing. This book stays in objective level,
    in dBFS — see [Status & scope](status.md).

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

For a sine wave, RMS sits about **3 dB below** the peak (that gap is its **crest factor**) — so
the choice of detector shifts your measured level. Most level effects in this book detect on one
of these and report the result as **dBFS (peak)** or **dBFS (RMS)** — always labelled, per the
convention above.

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
