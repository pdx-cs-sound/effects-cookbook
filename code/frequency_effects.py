"""Frequency-domain effects (Chapter 11).

This module is the single source for the chapter's code. The pages include
the marked sections at build time, and the figure generators import the
functions.

Standard library only. The spectral effects follow one pattern: analyze
with the Chapter 10 STFT, change the bins, resynthesize with the inverse.
"""

from transforms import istft, stft


# --8<-- [start:resample]
def resample(x, ratio):
    """Play the signal at a different rate: pitch and duration change
    together.

    Reads the input at fractional positions ratio apart, interpolating
    linearly as the vibrato of Chapter 7 does. A ratio of 2.0 halves the
    duration and doubles every frequency.
    """
    out = []
    pos = 0.0
    while pos < len(x) - 1:
        i = int(pos)
        frac = pos - i
        out.append((1.0 - frac) * x[i] + frac * x[i + 1])
        pos += ratio
    return out
# --8<-- [end:resample]


# --8<-- [start:spectral]
def spectral_lowpass(x, sr, cutoff, frame=512, hop=256):
    """Zero every bin above the cutoff, then resynthesize."""
    out = []
    for bins in stft(x, frame, hop):
        n = len(bins)
        kept = [0j] * n
        for k in range(n):
            f = min(k, n - k) * sr / n   # the upper bins mirror the lower
            if f <= cutoff:
                kept[k] = bins[k]
        out.append(kept)
    return istft(out, frame, hop)


def robotize(x, frame=512, hop=256):
    """Discard every bin's phase and keep the amplitudes.

    Each frame resynthesizes with all its content phase-aligned at the
    frame start, so the output pulses at the frame rate regardless of
    the input's pitch. On speech the result is the classic robot voice.
    """
    frames = [[abs(b) + 0j for b in bins] for bins in stft(x, frame, hop)]
    return istft(frames, frame, hop)
# --8<-- [end:spectral]
