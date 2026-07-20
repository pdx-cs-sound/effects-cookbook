"""Delay lines and the effects built from them (Chapter 7).

This module is the single source for the chapter's code. The pages include the
marked sections below at build time (pymdownx.snippets), and the figure and
demo generators import the functions, so page, figures, and sounds cannot
drift apart.

Standard library only. Signals are plain Python lists of floats in [-1.0, 1.0].
The reverberator follows Schroeder's design: four parallel feedback combs and
two series allpass stages.
"""

import math


# --8<-- [start:ringbuffer]
class RingBuffer:
    """Fixed-length memory for a delay line.

    Values are written into a fixed list, and a write position advances and
    wraps. Reading looks backward from the write position, also wrapping.
    Call read before push on each sample: read(d) then returns the value
    pushed d samples ago, for 1 <= d <= length, and returns 0.0 before
    anything has been written there.
    """

    def __init__(self, length):
        self.buf = [0.0] * length
        self.pos = 0

    def push(self, value):
        self.buf[self.pos] = value
        self.pos = (self.pos + 1) % len(self.buf)

    def read(self, delay):
        return self.buf[(self.pos - delay) % len(self.buf)]
# --8<-- [end:ringbuffer]


# --8<-- [start:echo]
def echo(x, sr, delay_ms=250.0, feedback=0.4, mix=0.5):
    """Repeating echo: the recirculated signal returns quieter each pass.

    x:  list of mono samples in [-1, 1]
    sr: sample rate, in samples per second
    Returns a new list of samples.
    """
    d = max(1, int(sr * delay_ms / 1000.0))
    line = RingBuffer(d)
    out = []
    for s in x:
        delayed = line.read(d)
        line.push(s + feedback * delayed)   # what recirculates
        out.append((1.0 - mix) * s + mix * delayed)
    return out
# --8<-- [end:echo]


# --8<-- [start:vibrato]
def vibrato(x, sr, rate_hz=5.0, depth_ms=2.0, base_ms=5.0):
    """Pitch wobble: an LFO sweeps a short delay, and the sweep shifts pitch.

    The delay is fractional, so the read interpolates linearly between the
    two nearest stored samples.
    """
    line = RingBuffer(int(sr * (base_ms + depth_ms) / 1000.0) + 2)
    out = []
    phase = 0.0
    step = rate_hz / sr
    for s in x:
        lfo = 0.5 + 0.5 * math.sin(2.0 * math.pi * phase)   # in [0, 1]
        delay = (base_ms + depth_ms * lfo) * sr / 1000.0
        i = int(delay)
        frac = delay - i
        delayed = (1.0 - frac) * line.read(i) + frac * line.read(i + 1)
        line.push(s)
        out.append(delayed)
        phase += step
        if phase >= 1.0:
            phase -= 1.0
    return out
# --8<-- [end:vibrato]


# --8<-- [start:chorus]
def chorus(x, sr, rate_hz=0.8, depth_ms=3.0, base_ms=20.0, mix=0.5):
    """A slowly detuned copy mixed with the original."""
    wet = vibrato(x, sr, rate_hz, depth_ms, base_ms)
    return [(1.0 - mix) * s + mix * w for s, w in zip(x, wet)]
# --8<-- [end:chorus]


# --8<-- [start:combs]
def comb(x, sr, delay_ms, feedback):
    """A feedback comb filter: one recirculating delay, output taken wet."""
    d = max(1, int(sr * delay_ms / 1000.0))
    line = RingBuffer(d)
    out = []
    for s in x:
        y = s + feedback * line.read(d)
        line.push(y)
        out.append(y)
    return out


def allpass(x, sr, delay_ms, g=0.7):
    """A Schroeder allpass stage: smears time while leaving levels flat."""
    d = max(1, int(sr * delay_ms / 1000.0))
    xline = RingBuffer(d)
    yline = RingBuffer(d)
    out = []
    for s in x:
        y = -g * s + xline.read(d) + g * yline.read(d)
        xline.push(s)
        yline.push(y)
        out.append(y)
    return out
# --8<-- [end:combs]


# --8<-- [start:reverb]
def reverb(x, sr, mix=0.3, decay=0.84):
    """Schroeder reverberator: four parallel combs, then two allpasses.

    The comb delays are spread and non-multiple so their echo patterns
    interleave instead of reinforcing.
    """
    wet = [0.0] * len(x)
    for ms in (29.7, 37.1, 41.1, 43.7):
        for i, v in enumerate(comb(x, sr, ms, decay)):
            wet[i] += 0.25 * v
    for ms in (5.0, 1.7):
        wet = allpass(wet, sr, ms)
    return [(1.0 - mix) * s + mix * w for s, w in zip(x, wet)]
# --8<-- [end:reverb]
