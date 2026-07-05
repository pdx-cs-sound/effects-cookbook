# Visualizations

An appendix collecting the interactive figures built for the cookbook. This is a testing
and feedback area, not part of the book proper: figures are tried out here first, and the
ones that earn their place get embedded into the relevant chapters. Each is a
self-contained, client-side demo — embedded below and also openable on its own page.

---

## Compressor design decision flow

A [POSA](https://en.wikipedia.org/wiki/Pattern-Oriented_Software_Architecture)-style map of the
choices you make when building a compressor: start with no design, pick one option per decision,
and end with a complete compressor. Toggle the buttons to overlay five real open-source
implementations — each is a different *path* through the same decisions, showing that "a
compressor" is a region of choices, not one algorithm.

<iframe src="../visualization/compressor_decision_map.html" title="Compressor design decision flow" loading="lazy" style="width:100%; height:720px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/compressor_decision_map.html" target="_blank" rel="noopener">Open full page ↗</a>

## AGC vs. limiter — static curve vs. time domain

Why a steady-state transfer curve **cannot** tell AGC from a limiter (they share one line),
while the time domain can: the slow AGC loop rides the whole envelope to a target, while the
fast limiter only shaves peaks. Companion to the [AGC](agc.md) page.

<iframe src="../visualization/agc_static_vs_time.html" title="AGC vs limiter, static transfer vs time domain" loading="lazy" style="width:100%; height:560px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/agc_static_vs_time.html" target="_blank" rel="noopener">Open full page ↗</a>

## Waveform & soft-clip distortion explorer

Pick a waveform (sine, sawtooth, square, triangle), adjust frequency and soft-clip depth, watch
the shape change, and hear the result. A hands-on feel for how clipping reshapes a signal.

<iframe src="../visualization/dsp_waveform_distortion_explorer.html" title="Waveform and soft-clip distortion explorer" loading="lazy" style="width:100%; height:600px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/dsp_waveform_distortion_explorer.html" target="_blank" rel="noopener">Open full page ↗</a>

## Audio waves & clipping

A Web Audio demo of basic waveforms and what clipping does to them — press play to listen.

<iframe src="../visualization/gemma_local_waves.html" title="Audio waves and clipping" loading="lazy" style="width:100%; height:560px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/gemma_local_waves.html" target="_blank" rel="noopener">Open full page ↗</a>

---

## Planned

*(Stubs for figures we've discussed but haven't built — to be filled in.)*

- A static **compressor transfer curve** (threshold / ratio / knee variants).
- A **crest factor / LUFS** "how do we measure it?" demo for the dynamics effects.
- An **envelope follower** (attack/release) demo for the [Conventions](conventions.md) page.
