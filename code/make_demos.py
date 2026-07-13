"""Generate the book's audio demos as WAV files.

Standard library only; every sample comes from oscillators.py, the same module
the Chapter 4 page includes and the figures are drawn from.

Run from the repository root:  python3 code/make_demos.py
Output:                        prototype/audio/*.wav  (served by MkDocs, committed)

Each demo gets a 10 ms linear fade at both ends: the square and sawtooth end
mid-cycle otherwise, and the truncation clicks.
"""

import os
import wave

from oscillators import (oscillator, sawtooth_shape, sine_shape, square_shape,
                         tremolo, triangle_shape)

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..",
                                        "prototype", "audio"))
SR = 44_100


def write_wav(path, samples, sr):
    """Write mono samples in [-1.0, 1.0] to path as a 16-bit WAV file."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        frames = bytearray()
        for s in samples:
            v = int(round(max(-1.0, min(1.0, s)) * 32767))
            frames += v.to_bytes(2, "little", signed=True)
        f.writeframes(bytes(frames))


def fade_ends(samples, sr, fade_ms=10.0):
    """Apply a linear fade-in and fade-out in place, and return the list."""
    n = min(int(sr * fade_ms / 1000.0), len(samples) // 2)
    for i in range(n):
        g = i / n
        samples[i] *= g
        samples[-1 - i] *= g
    return samples


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shapes = [("sine", sine_shape), ("square", square_shape),
              ("sawtooth", sawtooth_shape), ("triangle", triangle_shape)]
    combined = []
    gap = [0.0] * int(0.3 * SR)
    for name, shape in shapes:
        samples = fade_ends(oscillator(shape, 220.0, 1.5, SR, amp=0.5), SR)
        path = os.path.join(OUT_DIR, f"{name}_220hz.wav")
        write_wav(path, samples, SR)
        print(f"wrote {path}")
        combined += samples + gap
    # One file with all four in sequence, for uninterrupted comparison.
    path = os.path.join(OUT_DIR, "all_waveforms_220hz.wav")
    write_wav(path, combined[:-len(gap)], SR)
    print(f"wrote {path}")

    # Tremolo on a sine: the first effect demo.
    plain = oscillator(sine_shape, 220.0, 3.0, SR, amp=0.5)
    wobble = fade_ends(tremolo(plain, SR, rate_hz=5.0, depth=0.8), SR)
    path = os.path.join(OUT_DIR, "tremolo_220hz.wav")
    write_wav(path, wobble, SR)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
