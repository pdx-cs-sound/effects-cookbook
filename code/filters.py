"""FIR and IIR filters (Chapter 9).

This module is the single source for the chapter's code. The pages include
the marked sections at build time, and the figure generators import the
functions and measure their responses by running probe tones through them.

Standard library only. Signals are plain Python lists of floats. The FIR
filter reads its input history from the ring buffer of Chapter 7; the
biquad coefficient formulas follow Robert Bristow-Johnson's Audio EQ
Cookbook.
"""

import math

from delays import RingBuffer


# --8<-- [start:fir]
def fir(x, coeffs):
    """Finite impulse response: a weighted sum of recent input samples.

    y[n] = coeffs[0]*x[n] + coeffs[1]*x[n-1] + ... over len(coeffs) taps.
    """
    line = RingBuffer(len(coeffs))
    out = []
    for s in x:
        y = coeffs[0] * s
        for k in range(1, len(coeffs)):
            y += coeffs[k] * line.read(k)
        line.push(s)
        out.append(y)
    return out


def moving_average(n):
    """Equal FIR taps: the simplest lowpass."""
    return [1.0 / n] * n


FIRST_DIFFERENCE = [0.5, -0.5]   # the simplest highpass
# --8<-- [end:fir]


# --8<-- [start:onepole]
def one_pole(x, c):
    """The Chapter 5 smoother as a filter: feedback with one coefficient.

    y[n] = c * y[n-1] + (1 - c) * x[n], for 0 <= c < 1.
    """
    y = 0.0
    out = []
    for s in x:
        y = c * y + (1.0 - c) * s
        out.append(y)
    return out
# --8<-- [end:onepole]


# --8<-- [start:biquad]
def biquad(x, coeffs):
    """Two taps of input history and two of feedback: the standard audio IIR.

    coeffs is (b0, b1, b2, a1, a2), already normalized.
    """
    b0, b1, b2, a1, a2 = coeffs
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for s in x:
        y = b0 * s + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, s
        y2, y1 = y1, y
        out.append(y)
    return out


def rbj_lowpass(sr, freq, q=0.7071):
    """Lowpass biquad coefficients from the Audio EQ Cookbook."""
    w0 = 2.0 * math.pi * freq / sr
    alpha = math.sin(w0) / (2.0 * q)
    cw = math.cos(w0)
    a0 = 1.0 + alpha
    return ((1.0 - cw) / 2.0 / a0, (1.0 - cw) / a0, (1.0 - cw) / 2.0 / a0,
            -2.0 * cw / a0, (1.0 - alpha) / a0)


def rbj_highpass(sr, freq, q=0.7071):
    """Highpass biquad coefficients from the Audio EQ Cookbook."""
    w0 = 2.0 * math.pi * freq / sr
    alpha = math.sin(w0) / (2.0 * q)
    cw = math.cos(w0)
    a0 = 1.0 + alpha
    return ((1.0 + cw) / 2.0 / a0, -(1.0 + cw) / a0, (1.0 + cw) / 2.0 / a0,
            -2.0 * cw / a0, (1.0 - alpha) / a0)


def rbj_peaking(sr, freq, gain_db, q=1.0):
    """Peaking-EQ biquad coefficients from the Audio EQ Cookbook."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * freq / sr
    alpha = math.sin(w0) / (2.0 * q)
    cw = math.cos(w0)
    a0 = 1.0 + alpha / a
    return ((1.0 + alpha * a) / a0, -2.0 * cw / a0,
            (1.0 - alpha * a) / a0, -2.0 * cw / a0,
            (1.0 - alpha / a) / a0)


def rbj_allpass(sr, freq, q=0.7071):
    """Allpass biquad coefficients from the Audio EQ Cookbook."""
    w0 = 2.0 * math.pi * freq / sr
    alpha = math.sin(w0) / (2.0 * q)
    cw = math.cos(w0)
    a0 = 1.0 + alpha
    return ((1.0 - alpha) / a0, -2.0 * cw / a0, 1.0,
            -2.0 * cw / a0, (1.0 - alpha) / a0)
# --8<-- [end:biquad]


# --8<-- [start:filtereffects]
def equalizer(x, sr, bands):
    """Apply peaking-EQ bands in series.

    Each band is (center_frequency_hz, gain_db, q).
    Frequencies are between zero and sr/2, and q is positive.
    """
    out = list(x)
    for freq, gain_db, q in bands:
        out = biquad(out, rbj_peaking(sr, freq, gain_db, q))
    return out


def _swept_frequency(n, sr, low, high, rate, phase=0.0):
    """An LFO sweep on a logarithmic frequency scale."""
    position = 0.5 + 0.5 * math.sin(2.0 * math.pi * rate * n / sr + phase)
    return low * (high / low) ** position


def wah(x, sr, low=350.0, high=2200.0, rate=1.5, gain_db=15.0, q=2.5):
    """Sweep a resonant peaking filter between low and high.

    0 < low <= high < sr/2; rate is nonnegative and q is positive.
    """
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for n, s in enumerate(x):
        freq = _swept_frequency(n, sr, low, high, rate)
        b0, b1, b2, a1, a2 = rbj_peaking(sr, freq, gain_db, q)
        y = b0 * s + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, s
        y2, y1 = y1, y
        out.append(y)
    return out


def phaser(x, sr, low=300.0, high=1600.0, rate=0.4, q=0.5, stages=4):
    """Mix dry audio with a swept cascade of allpass biquads.

    0 < low <= high < sr/2; rate is nonnegative, q is positive, and
    stages is a positive integer.
    """
    states = [[0.0, 0.0, 0.0, 0.0] for _ in range(stages)]
    out = []
    for n, dry in enumerate(x):
        freq = _swept_frequency(n, sr, low, high, rate)
        coeffs = rbj_allpass(sr, freq, q)
        wet = dry
        for state in states:
            x1, x2, y1, y2 = state
            b0, b1, b2, a1, a2 = coeffs
            y = b0 * wet + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            state[:] = [wet, x1, y, y1]
            wet = y
        out.append(0.5 * (dry + wet))
    return out
# --8<-- [end:filtereffects]


# --8<-- [start:response]
def frequency_response(apply, sr, freqs, amp=0.5):
    """Measure a filter's gain at each frequency by running probe tones.

    apply is a function from a signal to a signal. Each probe plays for
    half a second; the first half of the output is discarded so the
    filter settles, and the Chapter 8 probe reads the amplitude that
    remains. The gain is output amplitude over input amplitude.
    """
    from frequency import sine_amount
    gains = []
    for f in freqs:
        n = int(0.5 * sr)
        probe = [amp * math.sin(2.0 * math.pi * f * i / sr)
                 for i in range(n)]
        y = apply(probe)[n // 2:]
        gains.append(sine_amount(y, sr, f) / amp)
    return gains
# --8<-- [end:response]
