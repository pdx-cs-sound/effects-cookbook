# Digital Audio Effects Cookbook

> An educational cookbook for digital audio effects. Each effect is explained at several
> levels — plain language, pseudocode, runnable code, and references — so a reader can
> work at the depth that suits them.

Written under PSU CS506 for CS416/516 students and self-educators. The goal is
understanding: what each effect does, why, and how to build one.

## Start here

The [Measuring sound](conventions.md) chapter defines the vocabulary the rest of the book
uses: samples, decibels, dBFS, gain, level detection. Read it first. The chapters after it
can be read in order or by topic.

## The chapters

Ordered by machinery: each chapter's effects need everything before them and nothing after.

1. **Introduction** — this page.
2. **[Measuring sound](conventions.md)** — samples, decibels, dBFS, gain, level detection.
3. **[Single-sample effects](single-sample.md)** — stateless: volume, distortion, bit
   crush.
4. **[Waveforms & oscillators](waveforms.md)** — sines and other waveforms, oscillators,
   LFOs.
5. **Envelopes & tremolo** — [Envelopes](envelopes.md), [Tremolo](tremolo.md).
6. **Companding** — [Compression](compression.md), [Limiting](limiter.md),
   [Expanding](expander.md), [AGC](agc.md).
7. **[Delay & modulation](delay-modulation.md)** — reverb, chorus, vibrato; ring buffers.
   *(planned)*
8. **[The frequency domain](frequency-domain.md)** — audio as frequencies. *(planned)*
9. **[Filters](filters.md)** — FIR and IIR. *(planned)*
10. **[DFT, FFT, STFT](transforms.md)** — the transforms. *(planned)*
11. **[Frequency-domain effects](frequency-effects.md)** — resampling, vocoding. *(planned)*

## How each effect page is laid out

Every effect page follows the same template: intuition in plain language, key parameters,
a mechanism walk-through, figures, pseudocode, a reference implementation in Python,
pitfalls, related effects, and references.

!!! note "Scope"
    Reference code is dependency-free Python meant to teach, not to ship; levels are in
    dBFS; the book stays in the digital domain. The full list of scope decisions and
    deferred topics is in [Status & scope](status.md).
