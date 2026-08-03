"""Tests for the Chapter 9 filters.

Run from the repo root:  python3 -m unittest discover -s code
"""

import math
import unittest

from filters import (FIRST_DIFFERENCE, biquad, fir, frequency_response,
                     moving_average, one_pole, rbj_highpass, rbj_lowpass)

SR = 8000


class TestFir(unittest.TestCase):
    def test_impulse_response_is_the_coefficient_list(self):
        x = [1.0] + [0.0] * 5
        self.assertEqual(fir(x, [0.5, 0.3, 0.2]), [0.5, 0.3, 0.2, 0, 0, 0])

    def test_moving_average_passes_a_constant_unchanged(self):
        y = fir([1.0] * 32, moving_average(8))
        self.assertAlmostEqual(y[-1], 1.0, places=9)

    def test_moving_average_cancels_its_null_frequency(self):
        # An 8-tap average nulls the tone with 8 samples per cycle.
        x = [0.5 * math.sin(2.0 * math.pi * n / 8.0) for n in range(400)]
        y = fir(x, moving_average(8))
        self.assertLess(max(abs(v) for v in y[8:]), 1e-9)

    def test_first_difference_blocks_a_constant(self):
        y = fir([1.0] * 16, FIRST_DIFFERENCE)
        self.assertAlmostEqual(y[-1], 0.0, places=9)


class TestOnePole(unittest.TestCase):
    def test_settles_on_a_constant_input(self):
        y = one_pole([1.0] * 4000, 0.99)
        self.assertAlmostEqual(y[-1], 1.0, places=3)

    def test_attenuates_high_frequencies_more_than_low(self):
        gains = frequency_response(lambda x: one_pole(x, 0.9), SR,
                                   [100.0, 2000.0])
        self.assertGreater(gains[0], gains[1] * 4)


class TestBiquad(unittest.TestCase):
    def test_lowpass_passes_low_and_blocks_high(self):
        coeffs = rbj_lowpass(SR, 500.0)
        gains = frequency_response(lambda x: biquad(x, coeffs), SR,
                                   [100.0, 500.0, 3000.0])
        self.assertAlmostEqual(gains[0], 1.0, delta=0.05)
        # At the cutoff with Q = 0.7071 the gain is 3 dB down.
        self.assertAlmostEqual(gains[1], 1.0 / math.sqrt(2.0), delta=0.05)
        self.assertLess(gains[2], 0.05)

    def test_highpass_mirrors_it(self):
        coeffs = rbj_highpass(SR, 500.0)
        gains = frequency_response(lambda x: biquad(x, coeffs), SR,
                                   [100.0, 3000.0])
        self.assertLess(gains[0], 0.1)
        self.assertAlmostEqual(gains[1], 1.0, delta=0.05)

    def test_resonance_peaks_at_the_cutoff(self):
        coeffs = rbj_lowpass(SR, 500.0, q=4.0)
        gains = frequency_response(lambda x: biquad(x, coeffs), SR,
                                   [100.0, 500.0])
        self.assertGreater(gains[1], 2.0)

    def test_impulse_response_decays(self):
        coeffs = rbj_lowpass(SR, 500.0)
        y = biquad([1.0] + [0.0] * (SR - 1), coeffs)
        self.assertLess(max(abs(v) for v in y[SR // 2:]), 1e-6)
