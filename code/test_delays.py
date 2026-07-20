"""Tests for the delay-line module.

Run from the repo root:  python3 -m unittest discover -s code
"""

import unittest

from delays import RingBuffer, allpass, chorus, comb, echo, reverb, vibrato
from oscillators import sine_wave

SR = 8000


def impulse(n):
    x = [0.0] * n
    x[0] = 1.0
    return x


class TestRingBuffer(unittest.TestCase):
    def test_reads_are_zero_before_writes(self):
        line = RingBuffer(4)
        self.assertEqual([line.read(d) for d in (1, 2, 3, 4)], [0.0] * 4)

    def test_read_returns_value_pushed_delay_ago(self):
        line = RingBuffer(4)
        for v in (1.0, 2.0, 3.0):
            line.push(v)
        self.assertEqual(line.read(1), 3.0)
        self.assertEqual(line.read(2), 2.0)
        self.assertEqual(line.read(3), 1.0)

    def test_wraps(self):
        line = RingBuffer(3)
        for v in (1.0, 2.0, 3.0, 4.0):
            line.push(v)
        self.assertEqual(line.read(1), 4.0)
        self.assertEqual(line.read(3), 2.0)


class TestEcho(unittest.TestCase):
    def test_impulse_taps_decay_by_the_feedback_factor(self):
        d = SR // 4                                     # 250 ms at 8000
        y = echo(impulse(3 * d + 1), SR, delay_ms=250.0, feedback=0.4, mix=0.5)
        self.assertAlmostEqual(y[0], 0.5, places=9)     # dry part
        self.assertAlmostEqual(y[d], 0.5, places=9)     # first repeat
        self.assertAlmostEqual(y[2 * d] / y[d], 0.4, places=9)
        self.assertAlmostEqual(y[3 * d] / y[2 * d], 0.4, places=9)

    def test_output_length_matches_input(self):
        x = sine_wave(220.0, 0.1, SR)
        self.assertEqual(len(echo(x, SR)), len(x))


class TestVibrato(unittest.TestCase):
    def test_zero_depth_is_a_pure_delay(self):
        x = sine_wave(220.0, 0.1, SR, amp=0.5)
        y = vibrato(x, SR, rate_hz=5.0, depth_ms=0.0, base_ms=5.0)
        d = SR * 5 // 1000                              # 40 samples exactly
        worst = max(abs(y[n] - x[n - d]) for n in range(d, len(x)))
        self.assertLess(worst, 1e-9)

    def test_output_stays_bounded(self):
        x = sine_wave(220.0, 0.2, SR, amp=0.5)
        y = vibrato(x, SR)
        self.assertLessEqual(max(abs(s) for s in y), 0.5 + 1e-9)


class TestChorus(unittest.TestCase):
    def test_mix_zero_is_identity(self):
        x = sine_wave(220.0, 0.1, SR, amp=0.5)
        y = chorus(x, SR, mix=0.0)
        self.assertLess(max(abs(a - b) for a, b in zip(x, y)), 1e-12)


class TestReverb(unittest.TestCase):
    def test_impulse_grows_a_decaying_tail(self):
        n = SR                                          # one second
        y = reverb(impulse(n), SR, mix=1.0)
        early = sum(v * v for v in y[: n // 4])
        late = sum(v * v for v in y[n // 2:])
        self.assertGreater(early, 0.0)
        self.assertGreater(late, 0.0)                   # a tail exists
        self.assertLess(late, early)                    # and it decays

    def test_stays_finite_and_length_preserving(self):
        x = sine_wave(220.0, 0.25, SR, amp=0.5)
        y = reverb(x, SR)
        self.assertEqual(len(y), len(x))
        self.assertLess(max(abs(s) for s in y), 4.0)

    def test_allpass_preserves_impulse_energy(self):
        n = SR // 2
        y = allpass(impulse(n), SR, 5.0)
        self.assertAlmostEqual(sum(v * v for v in y), 1.0, delta=0.01)

    def test_comb_rings_at_its_delay(self):
        d = max(1, int(SR * 29.7 / 1000.0))
        y = comb(impulse(3 * d), SR, 29.7, feedback=0.5)
        self.assertAlmostEqual(y[d], 0.5, places=9)
        self.assertAlmostEqual(y[2 * d], 0.25, places=9)


if __name__ == "__main__":
    unittest.main()
