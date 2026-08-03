"""Tests for the Chapter 8 frequency probe.

Run from the repo root:  python3 -m unittest discover -s code
"""

import math
import unittest

from frequency import sine_amount, spectrum
from oscillators import oscillator, sawtooth_shape, sine_wave, square_shape

SR = 8000


class TestSineAmount(unittest.TestCase):
    def test_reads_the_amplitude_of_a_matching_sine(self):
        x = sine_wave(440.0, 1.0, SR, amp=0.5)
        self.assertAlmostEqual(sine_amount(x, SR, 440.0), 0.5, places=6)

    def test_reads_near_zero_for_an_absent_frequency(self):
        x = sine_wave(440.0, 1.0, SR, amp=0.5)
        self.assertLess(sine_amount(x, SR, 1000.0), 1e-6)

    def test_phase_does_not_hide_the_signal(self):
        # A pure cosine has no correlation with the sine probe alone.
        x = [0.5 * math.cos(2.0 * math.pi * 440.0 * n / SR)
             for n in range(SR)]
        self.assertAlmostEqual(sine_amount(x, SR, 440.0), 0.5, places=6)

    def test_partial_cycles_leak(self):
        # Probing an absent frequency through a short window reads a
        # false amplitude; a window of whole cycles reads near zero.
        # The docstring's whole-cycles caveat, kept honest.
        short = sine_wave(440.0, 0.025, SR, amp=0.5)
        self.assertGreater(sine_amount(short, SR, 500.0), 0.01)
        whole = sine_wave(440.0, 1.0, SR, amp=0.5)
        self.assertLess(sine_amount(whole, SR, 500.0), 1e-6)


class TestWaveformSpectra(unittest.TestCase):
    def test_square_has_odd_harmonics_falling_as_one_over_n(self):
        f0 = 100.0
        x = oscillator(square_shape, f0, 1.0, SR)
        for n in (1, 3, 5, 7):
            with self.subTest(harmonic=n):
                got = sine_amount(x, SR, n * f0)
                self.assertAlmostEqual(got, 4.0 / (math.pi * n), delta=0.02)
        for n in (2, 4, 6):
            with self.subTest(harmonic=n):
                self.assertLess(sine_amount(x, SR, n * f0), 0.02)

    def test_sawtooth_has_every_harmonic_falling_as_one_over_n(self):
        f0 = 100.0
        x = oscillator(sawtooth_shape, f0, 1.0, SR)
        for n in (1, 2, 3, 4, 5):
            with self.subTest(harmonic=n):
                got = sine_amount(x, SR, n * f0)
                self.assertAlmostEqual(got, 2.0 / (math.pi * n), delta=0.02)

    def test_spectrum_lists_probes(self):
        x = sine_wave(200.0, 1.0, SR, amp=0.8)
        amps = spectrum(x, SR, [100.0, 200.0, 300.0])
        self.assertLess(amps[0], 1e-6)
        self.assertAlmostEqual(amps[1], 0.8, places=6)
        self.assertLess(amps[2], 1e-6)


class TestAliasing(unittest.TestCase):
    def test_a_tone_above_nyquist_lands_on_its_alias(self):
        # 9000 Hz sampled at 8000 produces the same samples as 1000 Hz.
        high = sine_wave(9000.0, 0.5, SR, amp=0.5)
        low = sine_wave(1000.0, 0.5, SR, amp=0.5)
        worst = max(abs(a - b) for a, b in zip(high, low))
        self.assertLess(worst, 1e-6)
