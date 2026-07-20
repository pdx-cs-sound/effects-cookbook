# Visualizations

An appendix collecting the interactive figures built for the cookbook. This is a testing
and feedback area rather than part of the book. Figures are tried here first, and the
ones that work get embedded into the relevant chapters. Each is a self-contained,
client-side demo, embedded below and also openable on its own page.

---

## Compressor design decision flow

A [POSA](https://en.wikipedia.org/wiki/Pattern-Oriented_Software_Architecture)-style map
of the decisions behind a compressor. A design starts from nothing, picks one option per
decision, and ends complete. The buttons overlay five open-source implementations, each a
different path through the same decisions, which shows that "a compressor" is a region of
choices rather than one algorithm.

<iframe src="../visualization/compressor_decision_map.html" title="Compressor design decision flow" loading="lazy" style="width:100%; height:820px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/compressor_decision_map.html" target="_blank" rel="noopener">Open full page ↗</a>

## AGC vs. limiter — static curve vs. time domain

A steady-state transfer curve cannot tell AGC from a limiter, since they share one line,
while the time domain can. The slow AGC loop rides the whole envelope to a target, and
the fast limiter only shaves peaks. Companion to the [AGC](agc.md) page.

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

## Tremolo AudioExplorer

The first AudioExplorer: the book's tremolo running live. The DSP is an AudioWorklet
port of `tremolo()` from `code/oscillators.py`, and a golden test in CI
(`code/test_worklet_ports.py`) compares the port against the Python sample by sample.
Press Play tone, adjust the sliders, and watch the last second of output under the
LFO-driven gain trace.

<iframe src="../visualization/tremolo_explorer.html" title="Tremolo AudioExplorer" loading="lazy" style="width:100%; height:560px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/tremolo_explorer.html" target="_blank" rel="noopener">Open full page ↗</a>

## Waveform AudioExplorer

The oscillators of [Chapter 4](waveforms.md) running live: pick one of five shapes
(including the reverse sawtooth, which sounds identical to the sawtooth), set volume and
frequency, and watch three cycles of the output. The frequency slider is wide enough
that the naive square and sawtooth alias audibly at the top. The DSP is an AudioWorklet
port of the chapter's oscillator and shape functions, golden-tested against the Python
in CI.

<iframe src="../visualization/waveform_explorer.html" title="Waveform AudioExplorer" loading="lazy" style="width:100%; height:560px; border:1px solid #d8d8d2; border-radius:8px;"></iframe>

<a href="../visualization/waveform_explorer.html" target="_blank" rel="noopener">Open full page ↗</a>

---

## Planned

One figure remains from the original list: a crest factor and LUFS measurement demo for
the companding effects. The other planned figures, the static transfer curves and the
envelope follower, shipped into their chapters.
