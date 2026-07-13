"""Tests for the oscillators module and the demo WAV writer.

Run from the repo root:  python3 -m unittest discover -s code
"""

import os
import tempfile
import unittest
import wave

from make_demos import fade_ends, write_wav
from oscillators import (burst_tone, follow, oscillator, sawtooth_shape,
                         sine_shape, sine_wave, square_shape, triangle_shape)

SR = 8000
ALL_SHAPES = (sine_shape, square_shape, sawtooth_shape, triangle_shape)


class TestShapes(unittest.TestCase):
    def test_every_shape_stays_in_range(self):
        for shape in ALL_SHAPES:
            samples = oscillator(shape, 100.0, 0.1, SR)
            self.assertLessEqual(max(abs(s) for s in samples), 1.0, shape.__name__)

    def test_amplitude_scales(self):
        samples = oscillator(square_shape, 100.0, 0.1, SR, amp=0.25)
        self.assertAlmostEqual(max(abs(s) for s in samples), 0.25, places=9)

    def test_square_has_exactly_two_levels(self):
        samples = oscillator(square_shape, 100.0, 0.1, SR)
        self.assertEqual(sorted(set(samples)), [-1.0, 1.0])

    def test_sawtooth_jumps_once_per_period(self):
        # 100 Hz at 8000 Hz: 80 samples per period, 10 periods in 0.1 s.
        samples = oscillator(sawtooth_shape, 100.0, 0.1, SR)
        jumps = sum(1 for a, b in zip(samples, samples[1:]) if abs(b - a) > 1.0)
        self.assertIn(jumps, (9, 10))

    def test_triangle_is_continuous(self):
        # The triangle's slope is 4 per period: 0.05 per sample here.
        samples = oscillator(triangle_shape, 100.0, 0.1, SR)
        worst = max(abs(b - a) for a, b in zip(samples, samples[1:]))
        self.assertLess(worst, 0.06)

    def test_phase_wraps_periodically(self):
        # Periodicity is asserted on the sine, which is smooth across the
        # wrap. Discontinuous shapes cannot be compared sample-exactly at the
        # period boundary: float phase accumulation can land the wrap one
        # sample late, and the sawtooth then differs by its full jump there
        # (a real property of float phase accumulators, noted on the page).
        samples = oscillator(sine_shape, 100.0, 0.1, SR)
        period = SR // 100
        for n in range(0, period):
            self.assertAlmostEqual(samples[n], samples[n + period], places=6)


class TestGenerators(unittest.TestCase):
    def test_sine_wave_matches_oscillator(self):
        a = sine_wave(220.0, 0.1, SR)
        b = oscillator(sine_shape, 220.0, 0.1, SR)
        worst = max(abs(x - y) for x, y in zip(a, b))
        self.assertLess(worst, 1e-6)

    def test_burst_tone_lengths_and_levels(self):
        x = burst_tone(SR, 220.0, [(0.1, 0.1), (0.1, 0.5), (0.1, 0.1)])
        self.assertEqual(len(x), int(0.3 * SR))
        mid = x[len(x) // 3: 2 * len(x) // 3]
        self.assertAlmostEqual(max(abs(s) for s in mid), 0.5, delta=0.01)

    def test_follow_rises_on_attack_and_decays_on_release(self):
        x = burst_tone(SR, 220.0, [(0.05, 0.0), (0.1, 0.5), (0.1, 0.0)])
        env = follow(x, 5.0, 50.0, SR)
        burst_end = int(0.15 * SR)
        self.assertGreater(env[burst_end - 1], 0.25)      # charged during burst
        self.assertLess(env[-1], env[burst_end - 1] / 2)  # decayed well after it


class TestWavWriter(unittest.TestCase):
    def test_round_trip(self):
        samples = fade_ends(sine_wave(220.0, 0.05, SR, amp=0.5), SR)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t.wav")
            write_wav(path, samples, SR)
            with wave.open(path, "rb") as f:
                self.assertEqual(f.getnchannels(), 1)
                self.assertEqual(f.getsampwidth(), 2)
                self.assertEqual(f.getframerate(), SR)
                self.assertEqual(f.getnframes(), len(samples))
                raw = f.readframes(f.getnframes())
        peak = max(abs(int.from_bytes(raw[i:i + 2], "little", signed=True))
                   for i in range(0, len(raw), 2))
        self.assertAlmostEqual(peak / 32767.0, 0.5, delta=0.01)


if __name__ == "__main__":
    unittest.main()
