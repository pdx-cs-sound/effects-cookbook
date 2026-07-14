# References

*Appendix. The sources that shaped the book, with context. Brief citations also appear at
the bottom of each chapter; entries here carry the explanation those one-liners cannot.*

## Five open-source compressors

The level-effects chapter was written against five open-source dynamic-range
implementations, spanning textbook code to shipping products. The
[design map](compression.md) plots each one as a path through the same decisions, and
the book's configurable compressor includes each as a preset. License terms are per
upstream project. Check before reusing code.

### dafx

`compexp.m`, about 34 lines of MATLAB, from the companion code to Zölzer's *DAFX* (see
[Texts](#texts)). A compressor and expander in a single expression: the gain curve is the
minimum of three slopes (unity, the compressor line, the expander line). RMS detection,
branched attack/release, a small alignment delay. It is teaching code, the clearest
statement of the algorithm in the set, and it is not real-time. The book's
[dynamic range control chapter page](https://www.dafx.de/DAFX_Book_Page_2nd_edition/chapter4.html)
and its [MATLAB downloads page](https://www.dafx.de/DAFX_Book_Page_2nd_edition/matlab.html)
both link the chapter's zipfile (`M_files_chap04.zip`), which contains `compexp.m` among
other files.

### pcs

A Python demonstration command-line compressor, about 90 lines, from the pdx-cs-sound
course materials:
[github.com/pdx-cs-sound/effects](https://github.com/pdx-cs-sound/effects/blob/master/compressor.py).
It processes disjoint blocks with a single gain per block, so it has no attack or release
state, and its peak detector measures peak-to-peak (`max − min`), which reads 6 dB hot.
Both properties make it a useful counter-example: it is the compressor referred to in
[Measuring sound](conventions.md)'s peak-to-peak warning, and the reason the design map has
"none" options for smoothing and ballistics.

### guitarix

A compressor written in about 80 lines of Faust, compiled to C++ inside the guitarix
guitar-amplifier simulator. Its soft knee interpolates the ratio linearly across the knee
width: continuous in value, with a slope kink at the knee's edge. The project keeps both
the Faust source and the generated C++ in its tree, so the same algorithm can be read in
human-maintained and machine-generated form.
[github.com/brummer10/guitarix](https://github.com/brummer10/guitarix)

### sox

The `compand` effect in SoX, about 570 lines of C. A general compander: the user supplies a
multi-segment transfer curve, and compression, expansion, and limiting all fall out of one
engine. Quadratic curve-fitting at the segment joints, per-channel envelopes, and
delay-based lookahead with end-of-stream drain handling.
[sox.sourceforge.net](https://sourceforge.net/projects/sox/) (`src/compand.c`)

### audacity

Audacity's compressor is an integration layer around Daniel Rudrich's SimpleCompressor
library: a quadratic soft knee whose slope is continuous through the knee, ballistics run
in the dB domain, and the one true look-ahead limiter in the set, where the gain
reduction ramps in early so it is fully in place when the transient arrives.
[github.com/audacity/audacity](https://github.com/audacity/audacity) · core:
[github.com/DanielRudrich/SimpleCompressor](https://github.com/DanielRudrich/SimpleCompressor)
(GPLv3)

## Standards

- ITU-R BS.1770 — loudness (LUFS) and true-peak (dBTP) measurement. The reason production
  limiters oversample. Free from [itu.int](https://www.itu.int/rec/R-REC-BS.1770).
- AES17 — measurement conventions for digital audio equipment, including the
  sine-referenced 0 dBFS RMS convention that this book declines (see
  [Measuring sound](conventions.md)).
- IEC 60268-8 — sound-system equipment. The anchor for Woodgate's distinctions between
  AGC, limiting, and compression.
- J. M. Woodgate, ISCVE Engineering Note 27.1, ["Automatic gain control, limiting and
  compression"](https://iscve.org.uk/wp-content/uploads/EngineeringNote-27.1-automatic-gain-control-limiting-and-compression.pdf)
  — two pages that separate the three effects by control-loop gain and release time; the
  basis of the taxonomy in the [AGC](agc.md) chapter.

## Texts

- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley, 2011. The standard
  reference for this book's subject matter.
- Julius O. Smith III, *Introduction to Digital Filters*,
  [ccrma.stanford.edu/~jos/filters](https://ccrma.stanford.edu/~jos/filters/) — free
  online; the background for one-pole smoothers and, later, the filter chapters.

The [Status & scope](status.md) page tracks the overall citation-verification state.
