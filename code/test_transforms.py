"""Tests for the Chapter 10 transforms.

Run from the repo root:  python3 -m unittest discover -s code
"""

import math
import unittest

from frequency import sine_amount
from oscillators import oscillator, sine_wave, square_shape
from transforms import dft, fft, hann, ifft, istft, magnitudes, stft

SR = 8000


class TestDftAndFft(unittest.TestCase):
    def test_fft_equals_dft(self):
        x = [math.sin(0.1 * m) + 0.3 * math.cos(0.7 * m) for m in range(64)]
        a = dft(x)
        b = fft(x)
        worst = max(abs(p - q) for p, q in zip(a, b))
        self.assertLess(worst, 1e-9)

    def test_a_bin_frequency_sine_reads_its_amplitude(self):
        n = 512
        k = 32
        x = [0.5 * math.sin(2.0 * math.pi * k * m / n) for m in range(n)]
        mags = magnitudes(fft(x))
        self.assertAlmostEqual(mags[k], 0.5, places=9)
        self.assertLess(max(mags[:k] + mags[k + 1:]), 1e-9)

    def test_ifft_inverts_fft(self):
        x = [math.sin(0.3 * m) for m in range(128)]
        y = ifft(fft(x))
        worst = max(abs(a - b) for a, b in zip(x, y))
        self.assertLess(worst, 1e-9)

    def test_fft_rejects_non_power_of_two(self):
        with self.assertRaises(ValueError):
            fft([0.0] * 96)


class TestWindow(unittest.TestCase):
    def test_hann_fades_in_and_out(self):
        w = hann(256)
        self.assertAlmostEqual(w[0], 0.0, places=12)
        self.assertAlmostEqual(w[128], 1.0, places=12)

    def test_window_reduces_leakage(self):
        # An off-bin sine: without a window the leaked amplitude far from
        # the tone is much larger than with the Hann window.
        n = 512
        f = 1023.0    # between bins at SR 8000 (bin spacing 15.625 Hz)
        x = [0.5 * math.sin(2.0 * math.pi * f * m / SR) for m in range(n)]
        w = hann(n)
        rect = magnitudes(fft(x))
        windowed = magnitudes(fft([v * wm for v, wm in zip(x, w)]))
        far = range(120, 200)   # bins well above the 1 kHz tone
        self.assertGreater(max(rect[k] for k in far),
                           10.0 * max(windowed[k] for k in far))


class TestStft(unittest.TestCase):
    def test_frame_count(self):
        x = [0.0] * SR
        self.assertEqual(len(stft(x, 512, 256)), (SR - 512) // 256 + 1)

    def test_istft_round_trip_is_identity_away_from_the_edges(self):
        x = sine_wave(300.0, 0.5, SR, amp=0.5)
        y = istft(stft(x, 512, 256), 512, 256)
        mid = range(512, len(y) - 512)
        worst = max(abs(x[m] - y[m]) for m in mid)
        self.assertLess(worst, 1e-9)
