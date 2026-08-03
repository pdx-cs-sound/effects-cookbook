"""Measuring frequency content (Chapter 8).

This module is the single source for the chapter's code. The pages include
the marked sections at build time, and the figure generators import the
functions.

Standard library only. Signals are plain Python lists of floats. The probe
here measures one frequency at a time; the transforms of Chapter 10 compute
every probe at once.
"""

import math


# --8<-- [start:probe]
def sine_amount(x, sr, freq):
    """How much of one frequency a signal contains.

    Multiply the signal by a probe sine and average, then do the same with
    a probe cosine. Either probe alone would miss a signal that is out of
    phase with it; together they catch every phase, and the magnitude of
    the pair is the amplitude of that frequency in the signal.

    Accurate when the signal covers whole cycles of freq.
    """
    s = 0.0
    c = 0.0
    for n, v in enumerate(x):
        angle = 2.0 * math.pi * freq * n / sr
        s += v * math.sin(angle)
        c += v * math.cos(angle)
    return 2.0 * math.sqrt(s * s + c * c) / len(x)
# --8<-- [end:probe]


# --8<-- [start:spectrum]
def spectrum(x, sr, freqs):
    """The amplitude of each listed frequency: one probe per entry."""
    return [sine_amount(x, sr, f) for f in freqs]
# --8<-- [end:spectrum]
