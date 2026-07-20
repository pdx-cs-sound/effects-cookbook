# Status & scope

This cookbook is an early prototype. Chapters, figures, and prose are still moving. This
page records what the book tries to be, what it leaves out, and what is deferred, so the
chapters themselves can stay about audio.

## What this book is

An educational cookbook for digital audio effects, written for CS416/516 students and
self-educators who want to go past the knobs and understand how the effects work. Each
effect gets the same treatment: plain-language intuition, key parameters, how it works,
pseudocode, a reference implementation in Python, pitfalls, and references for going
deeper.

## Scope decisions

- **Digital only.** No analog circuits and no analog explanations.
- **Teaching code, not production code.** Reference implementations favor clarity:
  standard library only, no numpy, no threading, no plugin scaffolding.
- **Levels are dBFS**, peak or RMS, always labeled. See [Conventions](conventions.md).
- **No AI-based effects**, and no coverage of AI-assisted use of these effects.

## Chapter status

The book follows an eleven-chapter plan (see the [Introduction](index.md)). Chapters 1
through 7 have drafted content. Chapters 8 through 11 are stubs. Drafted pages follow
the book's flat register.

## Deferred topics

- **Perceived loudness.** Phon, sone, LUFS (ITU-R BS.1770), A-weighting/dBA, and
  psychoacoustics generally. The book stays in objective signal level (dBFS).
- **Per-effect audio demos.** Before/after clips per effect are planned. The first
  generated demos (the waveform tones of [Chapter 4](waveforms.md)) set the pipeline.
  Samples come from the book's own code, rendered by `code/make_demos.py`.
- **Per-page visualizations.** Interactive figures are being tested in the
  [Visualizations](visualizations.md) appendix before being embedded in chapters.
- **Program-dependent ballistics.** Sketched in prose in the reference compressor's
  documentation, not implemented.

## Citations

References on the pages are starting points and are still being verified against the
project's attribution policy. Treat them as leads until this notice is removed.

## Where the design rationale lives

Motivation, decision history, and open questions are tracked in the repository rather
than in the book:
[DESIGN.md](https://github.com/pdx-cs-sound/effects-cookbook/blob/main/DESIGN.md) and the
notes under
[research/](https://github.com/pdx-cs-sound/effects-cookbook/tree/main/research).
