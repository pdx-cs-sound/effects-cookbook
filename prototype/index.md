# Digital Audio Effects Cookbook

> An educational, work-in-progress cookbook for **digital** audio effects. Each effect is
> explained at several levels — plain language, pseudocode, real (runnable) code, and links to
> go deeper — so you can learn it the way that suits you.

*Produced under PSU CS506 (with Massey); aimed at CS416/516 students and self-learners who want
to go past "turn this knob" and understand how these effects actually work.*

---

## Start here

New to this? Begin with the **[Conventions](conventions.md)** page — it sets up the shared
vocabulary (samples, dBFS, level detection, gain, attack/release) that every effect page builds
on. Then read the effects in either chapter.

## The chapters

Ordered by machinery: each chapter's effects need everything before them and nothing after.

1. **Introduction** — this page.
2. **[Measuring sound](conventions.md)** — samples, decibels, dBFS, gain, level detection.
3. **[Single-sample effects](single-sample.md)** — stateless: volume, distortion, mu-law,
   bit crush. *(planned)*
4. **[Waveforms & envelopes](waveforms.md)** — sines and other waveforms, oscillators,
   envelopes. *(partial)*
5. **Time domain: level** — [Tremolo](tremolo.md) *(planned)*,
   [Compression](compression.md), [Limiting](limiter.md), [Expanding](expander.md),
   [AGC](agc.md).
6. **[Delay & modulation](delay-modulation.md)** — reverb, chorus, vibrato; ring buffers.
   *(planned)*
7. **[The frequency domain](frequency-domain.md)** — audio as frequencies. *(planned)*
8. **[Filters](filters.md)** — FIR and IIR. *(planned)*
9. **[DFT, FFT, STFT](transforms.md)** — the transforms. *(planned)*
10. **[Frequency-domain effects](frequency-effects.md)** — resampling, vocoding. *(planned)*

## How each effect page is laid out

Every effect follows the same template: a plain-language **intuition**, the **key parameters**,
a **how it works** walk-through, **pseudocode**, a **reference implementation** in Python, the
**pitfalls**, related effects, and citations to learn more.

!!! note "Scope"
    Reference code is dependency-free Python meant to teach, not to ship; levels are in dBFS;
    the book stays in the digital domain. The full list of scope decisions and deferred
    topics is in [Status & scope](status.md).
