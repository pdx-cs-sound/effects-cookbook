"""Oscillators, waveforms, and the envelope follower (Chapter 4).

This module is the single source for the book's generated signals. The Chapter 4
page includes the marked sections below verbatim at build time (pymdownx.snippets,
the same mechanism as the compressor design page), `make_figures.py` imports the
functions to draw the waveform and envelope figures, and `make_demos.py` imports
them to render the audio demos. Page, figures, and demos cannot drift apart.

Standard library only. Signals are plain Python lists of floats in [-1.0, 1.0].
"""

import math


# --8<-- [start:sine]
def sine_wave(freq, dur, sr, amp=1.0):
    """A sine tone: amp * sin(2*pi*freq*t), for dur seconds at rate sr."""
    return [amp * math.sin(2.0 * math.pi * freq * n / sr)
            for n in range(int(dur * sr))]
# --8<-- [end:sine]


# --8<-- [start:oscillator]
def oscillator(shape, freq, dur, sr, amp=1.0):
    """Run a shape function over a phase that climbs from 0 to 1 and wraps.

    shape: a function from phase in [0, 1) to a sample in [-1, 1].
    """
    out = []
    phase = 0.0
    step = freq / sr
    for _ in range(int(dur * sr)):
        out.append(amp * shape(phase))
        phase += step
        if phase >= 1.0:
            phase -= 1.0
    return out
# --8<-- [end:oscillator]


# --8<-- [start:shapes]
def sine_shape(phase):
    return math.sin(2.0 * math.pi * phase)


def square_shape(phase):
    return 1.0 if phase < 0.5 else -1.0


def sawtooth_shape(phase):
    return 2.0 * phase - 1.0


def triangle_shape(phase):
    return 4.0 * phase - 1.0 if phase < 0.5 else 3.0 - 4.0 * phase
# --8<-- [end:shapes]


# --8<-- [start:follow]
def smoothing_coeff(time_ms, sr):
    """One-pole coefficient for a given time constant at sample rate sr."""
    return math.exp(-1.0 / (sr * time_ms / 1000.0))


def follow(signal, attack_ms, release_ms, sr):
    """Trace a signal's envelope: fast up (attack), slow down (release)."""
    atk = smoothing_coeff(attack_ms, sr)
    rel = smoothing_coeff(release_ms, sr)
    env = 0.0
    out = []
    for s in signal:
        target = abs(s)
        coeff = atk if target > env else rel   # attack when rising, release when falling
        env = coeff * env + (1.0 - coeff) * target
        out.append(env)
    return out
# --8<-- [end:follow]


# --8<-- [start:tremolo]
def tremolo(x, sr, rate_hz=5.0, depth=0.5):
    """Multiply the signal by an LFO-driven gain between 1 - depth and 1."""
    out = []
    phase = 0.0
    step = rate_hz / sr
    for s in x:
        m = 0.5 + 0.5 * math.sin(2.0 * math.pi * phase)   # LFO in [0, 1]
        out.append(s * (1.0 - depth * m))
        phase += step
        if phase >= 1.0:
            phase -= 1.0
    return out
# --8<-- [end:tremolo]


def burst_tone(sr, freq, sections):
    """Sine tone whose amplitude steps through (duration_s, amplitude) sections.

    The quiet-loud-quiet test signal behind the book's time-domain figures.
    """
    out = []
    n = 0
    for dur, amp in sections:
        for _ in range(int(dur * sr)):
            out.append(amp * math.sin(2 * math.pi * freq * n / sr))
            n += 1
    return out
