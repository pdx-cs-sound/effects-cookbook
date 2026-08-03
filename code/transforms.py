"""The DFT, FFT, and STFT (Chapter 10).

This module is the single source for the chapter's code. The pages include
the marked sections at build time, and the figure generators import the
functions.

Standard library only; the complex arithmetic uses cmath. Signals are
plain Python lists of floats, spectra are lists of complex bins.
"""

import cmath
import math


# --8<-- [start:dft]
def dft(x):
    """Every Chapter 8 probe at once.

    For a block of N samples, bin k correlates the block with frequency
    k * sr / N: the real part comes from a cosine probe and the
    imaginary part from a sine probe, so each bin holds an amplitude and
    a phase together.
    """
    n = len(x)
    return [sum(x[m] * cmath.exp(-2j * cmath.pi * k * m / n)
                for m in range(n))
            for k in range(n)]


def magnitudes(bins):
    """Bin amplitudes on the Chapter 8 scale: a full-scale sine at a bin
    frequency reads 1.0. Bins above N/2 mirror the ones below it."""
    n = len(bins)
    return [2.0 * abs(b) / n for b in bins[:n // 2]]
# --8<-- [end:dft]


# --8<-- [start:fft]
def fft(x):
    """The same bins as dft, computed in N log N steps (Cooley-Tukey).

    The length must be a power of two. The split works because the
    even-indexed and odd-indexed samples each form a half-length
    transform, and every full-length bin is one twiddle-factor
    combination of the two.
    """
    n = len(x)
    if n == 1:
        return [complex(x[0])]
    if n % 2:
        raise ValueError("fft needs a power-of-two length")
    even = fft(x[0::2])
    odd = fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        tw = cmath.exp(-2j * cmath.pi * k / n) * odd[k]
        out[k] = even[k] + tw
        out[k + n // 2] = even[k] - tw
    return out


def ifft(bins):
    """Samples back from bins: the inverse transform."""
    n = len(bins)
    swapped = fft([b.conjugate() for b in bins])
    return [s.conjugate().real / n for s in swapped]
# --8<-- [end:fft]


# --8<-- [start:window]
def hann(n):
    """The Hann window: a raised cosine that fades a frame in and out."""
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * m / n) for m in range(n)]
# --8<-- [end:window]


# --8<-- [start:stft]
def stft(x, frame=512, hop=256):
    """Windowed FFTs of overlapping frames: spectra over time."""
    w = hann(frame)
    frames = []
    pos = 0
    while pos + frame <= len(x):
        frames.append(fft([x[pos + m] * w[m] for m in range(frame)]))
        pos += hop
    return frames


def istft(frames, frame=512, hop=256):
    """Overlap-add resynthesis.

    With the Hann window and hop = frame / 2, the shifted windows sum to
    one, so away from the first and last half frame the signal returns
    exactly.
    """
    n = hop * (len(frames) - 1) + frame
    out = [0.0] * n
    for i, bins in enumerate(frames):
        y = ifft(bins)
        for m in range(frame):
            out[i * hop + m] += y[m]
    return out
# --8<-- [end:stft]
