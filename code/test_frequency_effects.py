"""Tests for the Chapter 11 frequency-domain effects.

Run from the repo root:  python3 -m unittest discover -s code
"""

import unittest

from frequency import sine_amount
from frequency_effects import resample, robotize, spectral_lowpass
from oscillators import sine_wave

SR = 8000


class TestResample(unittest.TestCase):
    def test_ratio_two_halves_length_and_doubles_pitch(self):
        x = sine_wave(400.0, 1.0, SR, amp=0.5)
        y = resample(x, 2.0)
        self.assertAlmostEqual(len(y), len(x) / 2, delta=2)
        self.assertAlmostEqual(sine_amount(y, SR, 800.0), 0.5, delta=0.01)

    def test_ratio_half_doubles_length_and_halves_pitch(self):
        x = sine_wave(400.0, 1.0, SR, amp=0.5)
        y = resample(x, 0.5)
        self.assertAlmostEqual(len(y), len(x) * 2, delta=2)
        self.assertAlmostEqual(sine_amount(y, SR, 200.0), 0.5, delta=0.01)


class TestSpectralLowpass(unittest.TestCase):
    def test_keeps_the_low_tone_and_removes_the_high_one(self):
        low = sine_wave(300.0, 1.0, SR, amp=0.4)
        high = sine_wave(2500.0, 1.0, SR, amp=0.4)
        x = [a + b for a, b in zip(low, high)]
        y = spectral_lowpass(x, SR, 1000.0)
        mid = y[1024:-1024]
        self.assertAlmostEqual(sine_amount(mid, SR, 300.0), 0.4, delta=0.02)
        self.assertLess(sine_amount(mid, SR, 2500.0), 0.02)


class TestRobotize(unittest.TestCase):
    def test_output_is_sane_and_periodic_at_the_frame_rate(self):
        x = sine_wave(313.0, 0.5, SR, amp=0.5)
        y = robotize(x, 512, 256)
        peak = max(abs(v) for v in y)
        self.assertGreater(peak, 0.05)
        self.assertLess(peak, 1.5)
        # Phase discard aligns every frame the same way, so the middle of
        # the output repeats with period equal to the hop.
        mid = y[1024:2048]
        shifted = y[1024 + 256:2048 + 256]
        worst = max(abs(a - b) for a, b in zip(mid, shifted))
        self.assertLess(worst, 1e-4)
