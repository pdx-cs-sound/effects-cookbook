# Measuring sound

> The shared vocabulary the rest of this cookbook leans on: how audio is represented, how
> level is measured in dBFS, and how linear gain and decibel gain convert. Every later
> chapter assumes these.

*Chapter 2 — how this book measures and talks about sound.*

---

## Audio as samples

Digital audio is a list of numbers. The signal's amplitude is measured many thousands of
times per second and each measurement is stored as one sample. The measurement rate is
called the sample rate, written `sr` and measured in samples per second; 44 100 and
48 000 are common. Other sources write sample rates in hertz, as in 44.1 kHz. It is the
same quantity. This book reserves hertz for the frequency of a tone and uses samples per
second for how often the signal is measured, so that the two stay visibly distinct when
later chapters relate them.

Throughout this cookbook a mono signal is a plain Python list of floats in the range
[-1.0, 1.0]:

- `0.0` is the resting value, the center of the range,
- `+1.0` and `-1.0` are the largest values the format can represent, called full scale,
- values beyond ±1.0 clip (distort) on playback.

A single sample has no loudness. Sound is variation over time, so silence and loudness are
properties of a stretch of samples, not of one value. A signal that stays at 0.0 is
silent. A full-scale sine passes through 0.0 twice per cycle while being as loud as the
format allows.

```python
# One second of a 440 Hz sine at half amplitude, 48 000 samples per second.
import math

sr = 48_000
signal = [0.5 * math.sin(2 * math.pi * 440 * n / sr) for n in range(sr)]
```

!!! note "Why [-1, 1]?"
    The range is format-independent: the math is the same whether the file is later
    rendered to 16-bit, 24-bit, or anything else. This book never works in raw integer
    sample values.

!!! note "Why mono only?"
    A stereo effect is usually the mono effect applied to each channel, sometimes with a
    shared control signal (a stereo compressor often drives both channels from one
    detector, so the image does not wander). Little is lost by working in mono, and every
    algorithm in this book extends to stereo by running it per channel.

## Measuring level: decibels and dBFS

Signal levels span a large range, so they are measured logarithmically, in decibels (dB).
Three details matter, and everyday usage blurs all of them. A dB is always relative to a
reference. The formula differs for power and for amplitude. A dBFS figure means nothing
until peak or RMS is specified.

### A decibel is a ratio and needs a reference

A decibel is dimensionless. It compares a measured value against a fixed reference:

$$
\mathrm{dB} = 10 \log_{10}\!\left(\frac{\text{measured}}{\text{reference}}\right)
$$

This is the form for power quantities. The amplitude form follows below.

- The numerator is the quantity being measured; the denominator is a fixed, agreed
  reference.
- Without a fixed reference, a dB is a relative change. Gain is stated this way (+6 dB
  is ×2 in amplitude). With a standard reference, a dB names an absolute level, and the
  suffix names the reference: dBFS, dB SPL.

A bare "dB" is never a level. The referenced unit pins down both the reference and the
power-versus-amplitude question below.

### Power vs. amplitude: 10·log and 20·log

The reference must match the kind of quantity, and that sets the multiplier:

- Power quantities (intensity, electrical power): $\mathrm{dB} = 10 \log_{10}(P / P_0)$.
- Amplitude, or field, quantities (sound pressure, voltage, sample values):
  $\mathrm{dB} = 20 \log_{10}(A / A_0)$. The 20 appears because power is proportional to
  the square of amplitude, $P \propto A^2$.

The two forms agree on the same physical change: doubling the amplitude and quadrupling
the power are both +6 dB. The dB value therefore never tells which quantity was measured;
the unit does:

| Unit | Measures | Reference | Quantity → factor | Domain |
|---|---|---|---|---|
| dBFS | sample amplitude | full scale (1.0) | amplitude → 20·log | digital, absolute |
| dB SPL | sound pressure | 20 µPa | amplitude → 20·log | acoustic, absolute |
| dBV / dBu | voltage | 1 V / 0.775 V RMS | amplitude → 20·log | electrical, absolute |
| dBm | electrical power | 1 mW | power → 10·log | electrical, absolute |
| dB SIL / SWL | sound intensity / power | 10⁻¹² W/m² · W | power → 10·log | acoustic, absolute |
| dB (gain) | a change | the other signal | match the quantity | relative |

The units audio work touches most often (dBFS, dB SPL, dBV, dBu) are amplitude quantities,
so the 20·log form is this book's default.

### dBFS

This book works on samples, so the reference is full scale (amplitude 1.0) and the unit is
dBFS, decibels relative to full scale. Samples are amplitudes, so the 20·log form
applies:

$$
\mathrm{dBFS} = 20 \log_{10}\frac{|x[n]|}{1.0}
$$

- amplitude 1.0 → 0 dBFS, the loudest representable level,
- everything quieter is negative (0.5 → −6 dBFS),
- amplitude 0.0 → −∞ dBFS. The logarithm of zero is undefined, so the code below
  returns −∞.

| Linear amplitude | dBFS |
|---|---|
| 1.0 | 0 |
| 0.5 | −6.0 |
| 0.25 | −12.0 |
| 0.1 | −20.0 |
| 0.01 | −40.0 |
| 0.001 | −60.0 |

Two rules of thumb fall out of the math: halving the amplitude is about −6 dB, and
dividing it by ten is exactly −20 dB.

```python
import math

def db_from_amplitude(a):
    """Linear amplitude -> dBFS. Zero amplitude maps to -inf."""
    a = abs(a)
    return 20.0 * math.log10(a) if a > 0.0 else float("-inf")

def amplitude_from_db(db):
    """dBFS -> linear amplitude."""
    return 10.0 ** (db / 20.0)
```

### Peak vs. RMS dBFS

A dBFS figure is under-specified until the detector is named, because the number depends
on how the signal is reduced to one value. The reference is always full scale (1.0). The
detector is always labeled:

- dBFS (peak): the instantaneous sample magnitude, $20 \log_{10}|x[n]|$. Sample peak
  cannot exceed 0 dBFS. This is the book's primary unit; the per-sample detectors report
  it.
- dBFS (RMS): the energy average over a window, $20 \log_{10}(\mathrm{rms})$, against the
  same 1.0 reference.

A full-scale sine reads 0 dBFS (peak) and −3.01 dBFS (RMS). The 3 dB gap is the signal's
crest factor. Both readings use the same reference, so the RMS figure is whatever the
formula produces, with no meter convention added.

!!! example "Worked example: the −3.01 dB of a full-scale sine"
    Take a sine with peak amplitude 1.0. There are two correct routes to its RMS level,
    and one common mistake.

    - Amplitude route. The RMS amplitude is $1/\sqrt{2} \approx 0.707$. Amplitude takes
      the 20 multiplier: $20 \log_{10}(0.707) = -3.01$ dBFS (RMS).
    - Power route. The mean power is the square of the RMS amplitude: $0.707^2 = 0.5$.
      Power takes the 10 multiplier: $10 \log_{10}(0.5) = -3.01$ dB. The two routes
      agree; the 10/20 convention exists so that they do.
    - The mistake. Pairing the amplitude value with the power multiplier,
      $10 \log_{10}(0.707)$, gives $-1.5$ dB. A result at exactly half (or double) the
      expected value usually means a 10/20 mix-up.

    The phrase "RMS power" usually sets this trap. RMS is an amplitude, and its square is
    the power. Saying "RMS amplitude" (0.707) or "mean power" (0.5) chooses the multiplier
    automatically.

!!! note "This book does not use the AES17 RMS offset"
    Broadcast meters (AES17) re-reference RMS so that a full-scale sine reads 0 dBFS RMS,
    a fixed +3.01 dB offset; a full-scale square then reads +3 dBFS RMS. This book does
    not use the offset, because it hides the crest factor behind a constant. The cost is
    that the
    book's RMS numbers sit about 3 dB below what a typical DAW meter shows.

### Peak-to-peak

Peak-to-peak amplitude is the full vertical span of a waveform, $\max - \min$. For a
symmetric signal it is twice the peak; in this book's range it reaches 2.0. The
measurement is legitimate where the span itself is the quantity of interest. An
oscilloscope reports peak-to-peak because the screen shows the span. Electrical
interfaces specify voltage swings peak-to-peak. A nonzero mean (a DC offset) shows up as
asymmetry between max and min.

Peak-to-peak is not a level. A level compares a magnitude against the full-scale
reference, and the span is not a magnitude. A detector that uses $\max - \min$ reads 6 dB
hot next to a true peak detector, since $20 \log_{10} 2 \approx 6.02$, and a DC offset
inflates the span further without making anything louder. One of the open-source
compressors surveyed for this book makes exactly this mistake. Level is the magnitude
$|x[n]|$ (peak) or the RMS, never the span. A sanity check for any level reading:
RMS ≤ peak ≤ 1.0, so no reading in this system can exceed 0 dBFS.

### Level vs. loudness vs. volume

These three words are often used interchangeably. They name different things:

- Level: an objective signal measure, in dB. When this book says "louder," it means higher
  level in dB.
- Loudness: how loud a sound seems. A perceptual quantity, nonlinearly related to level.
  +6 dB is not "twice as loud."
- Volume: not a measurement. A control; a gain setting.

"Double it" is three different requests:

| "Double it" means… | dB change | amplitude | power |
|---|---|---|---|
| ×2 amplitude | +6 dB | ×2 | ×4 |
| ×2 power | +3 dB | ×1.41 | ×2 |
| ×2 perceived loudness | ≈ +10 dB | ×3.16 | ×10 |

The loudness row is a psychoacoustic rule of thumb (Stevens' sone scale), not an exact
law.

!!! note "Loudness is deferred"
    Perceived loudness has its own units (phon, sone) and an engineering proxy (LUFS), all
    of which need sound-pressure levels and models of hearing. This book stays in
    objective level, in dBFS. See [Status & scope](status.md).

## Gain: linear and in dB

Gain is multiplication. To change a signal's level, every sample is multiplied by a
constant. A gain of 1.0 changes nothing. A gain of 0.5 halves the amplitude (−6 dB),
and a gain of 2.0 doubles it (+6 dB).

Gain is discussed in dB and applied linearly, so every effect converts between the two:

```python
def apply_gain_db(signal, gain_db):
    """Return a new signal scaled by gain_db (in dB)."""
    g = amplitude_from_db(gain_db)        # dB -> linear, once
    return [s * g for s in signal]
```

!!! warning "Keep dB and linear straight"
    Decibels add. Linear gains multiply. Two stages of +6 dB give +12 dB, which is ×4 in
    linear terms. Mixing the two domains is the most common beginner bug.

## Detecting level: peak vs. RMS

An effect that reacts to the current level first needs a number for it. Two detectors are
common:

- Peak: the largest magnitude in a window. It reacts to transients and is the right
  detector for preventing clipping.
- RMS: the square root of the mean of the squared samples over a window. It is smoother,
  and by rule of thumb it is closer to perceived loudness than peak.

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

For a sine wave, RMS sits about 3 dB below peak, and the gap is the crest factor. The
choice of detector shifts the measured level, so readings are always labeled dBFS (peak)
or dBFS (RMS).

Following a level over time is covered in [Chapter 5](envelopes.md), with attack,
release, and the one-pole envelope follower.

## Pitfalls

!!! warning "Common mistakes"
    - `log10(0)` is undefined. Guard zero amplitude before taking a logarithm; the code above
      returns −∞.
    - dB is not linear. Convert deliberately, and never add a dB value to a sample.
    - Detector choice matters. Peak and RMS of the same signal differ by several dB.
      State which one a measurement uses.

## Learn more

- [dBFS](https://en.wikipedia.org/wiki/DBFS) and [Decibel](https://en.wikipedia.org/wiki/Decibel) — Wikipedia, for the measurement basics.
- [Root mean square](https://en.wikipedia.org/wiki/Root_mean_square) — Wikipedia.
- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley, 2011 — the standard reference for this cookbook.
- Julius O. Smith III, *Introduction to Digital Filters*, CCRMA (free online) — for one-pole smoothers.
