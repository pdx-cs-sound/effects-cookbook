"""Tests for the configurable compressor (stdlib unittest, no dependencies).

Run from the repo root:   python3 -m unittest discover -s code -v
or from code/:            python3 -m unittest test_compressor -v

The assertions are signal-level facts a compressor must satisfy (unity below
threshold, ratio math above it, ceilings, attack/release direction), plus the
"granularity" claim from the decision map: all five presets produce different
output on the same program material.
"""

import math
import unittest

from compressor import (PRESETS, amplitude_from_db, compress,
                        db_from_amplitude, knee_hard, knee_soft_linear,
                        knee_soft_quad)

SR = 8000  # small rate keeps the pure-Python loops fast


def sine(freq=440.0, dur=0.25, amp=1.0, sr=SR):
    return [amp * math.sin(2 * math.pi * freq * n / sr)
            for n in range(int(dur * sr))]


def burst(quiet_db=-40.0, loud_db=-3.0, dur=0.3, sr=SR):
    """Quiet sine with a loud middle section (a step up, then back down)."""
    q, l = amplitude_from_db(quiet_db), amplitude_from_db(loud_db)
    n_total = int(dur * sr)
    third = n_total // 3
    return [(l if third <= n < 2 * third else q)
            * math.sin(2 * math.pi * 440.0 * n / sr) for n in range(n_total)]


def peak_db(seg):
    return db_from_amplitude(max(abs(s) for s in seg))


def tail(x, frac=0.25):
    return x[int(len(x) * (1.0 - frac)):]


class TestConversions(unittest.TestCase):
    def test_round_trip(self):
        for db in (-60.0, -6.02, 0.0):
            self.assertAlmostEqual(
                db_from_amplitude(amplitude_from_db(db)), db, places=9)

    def test_silence_is_neg_inf(self):
        self.assertEqual(db_from_amplitude(0.0), float("-inf"))


class TestKneeFunctions(unittest.TestCase):
    RATIO, KNEE = 4.0, 6.0
    SLOPE = 1.0 / RATIO - 1.0

    def test_all_zero_below_knee(self):
        for fn in (knee_hard, knee_soft_quad, knee_soft_linear):
            self.assertEqual(fn(-10.0, self.RATIO, self.KNEE), 0.0)

    def test_all_match_hard_line_above_knee(self):
        over = 12.0
        expected = self.SLOPE * over
        for fn in (knee_hard, knee_soft_quad, knee_soft_linear):
            self.assertAlmostEqual(fn(over, self.RATIO, self.KNEE),
                                   expected, places=9)

    def test_quad_is_continuous_at_knee_edges(self):
        half = self.KNEE / 2.0
        eps = 1e-6
        for edge in (-half, half):
            below = knee_soft_quad(edge - eps, self.RATIO, self.KNEE)
            above = knee_soft_quad(edge + eps, self.RATIO, self.KNEE)
            self.assertAlmostEqual(below, above, places=4)

    def test_quad_softens_the_corner(self):
        # At the threshold the hard knee is 0; the spline is already reducing.
        at0 = knee_soft_quad(0.0, self.RATIO, self.KNEE)
        self.assertAlmostEqual(at0, self.SLOPE * self.KNEE / 8.0, places=9)
        self.assertLess(at0, 0.0)

    def test_linear_blend_is_continuous_and_kinked(self):
        eps = 1e-6
        # Continuous in value at the knee's upper edge...
        below = knee_soft_linear(self.KNEE - eps, self.RATIO, self.KNEE)
        above = knee_soft_linear(self.KNEE + eps, self.RATIO, self.KNEE)
        self.assertAlmostEqual(below, above, places=4)
        # ...but the slope jumps there (the guitarix kink), unlike the spline.
        def slope_at(fn, over):
            h = 1e-4
            return (fn(over + h, self.RATIO, self.KNEE)
                    - fn(over - h, self.RATIO, self.KNEE)) / (2 * h)
        lin_jump = abs(slope_at(knee_soft_linear, self.KNEE + 1e-3)
                       - slope_at(knee_soft_linear, self.KNEE - 1e-3))
        quad_jump = abs(slope_at(knee_soft_quad, self.KNEE / 2 + 1e-3)
                        - slope_at(knee_soft_quad, self.KNEE / 2 - 1e-3))
        self.assertGreater(lin_jump, 0.05)      # kinked
        self.assertLess(quad_jump, 0.005)       # tangent

    def test_infinite_ratio_is_a_limiter_not_a_nan(self):
        for fn in (knee_hard, knee_soft_quad, knee_soft_linear):
            red = fn(5.0, math.inf, self.KNEE)
            self.assertFalse(math.isnan(red))
        self.assertAlmostEqual(knee_hard(5.0, math.inf, 0.0), -5.0, places=9)


class TestCompressorBasics(unittest.TestCase):
    def test_silence_in_silence_out_all_presets(self):
        x = [0.0] * 512
        for name, preset in PRESETS.items():
            y = compress(x, SR, **preset)
            self.assertEqual(len(y), len(x), name)
            self.assertLessEqual(max(abs(s) for s in y), 1e-12, name)

    def test_below_threshold_is_bit_exact_unity(self):
        x = sine(amp=amplitude_from_db(-40.0))
        y = compress(x, SR, threshold_db=-20.0, knee="hard")
        self.assertEqual(len(y), len(x))
        self.assertLess(max(abs(a - b) for a, b in zip(x, y)), 1e-12)

    def test_hard_knee_ratio_math(self):
        # -6.02 dBFS peak in, threshold -20, ratio 4 =>
        # out peak = -20 + 13.98/4 = -16.5 dBFS. ballistics="none" makes the
        # gain exact at the sine's peak sample.
        x = sine(amp=0.5)
        y = compress(x, SR, threshold_db=-20.0, ratio=4.0, knee="hard",
                     ballistics="none")
        expected = -20.0 + (db_from_amplitude(0.5) + 20.0) / 4.0
        self.assertAlmostEqual(peak_db(y), expected, delta=0.02)

    def test_output_has_no_nan_or_inf(self):
        x = burst()
        for name, preset in PRESETS.items():
            y = compress(x, SR, **preset)
            self.assertTrue(all(math.isfinite(s) for s in y), name)


class TestBallisticsAndTopology(unittest.TestCase):
    def test_faster_attack_clamps_sooner(self):
        x = burst()
        third = len(x) // 3
        onset = slice(third, third + int(0.005 * SR))  # 5 ms after the step
        fast = compress(x, SR, attack_ms=0.5, release_ms=50.0)
        slow = compress(x, SR, attack_ms=20.0, release_ms=50.0)
        self.assertLess(peak_db(fast[onset]), peak_db(slow[onset]))

    def test_release_recovers_toward_unity(self):
        x = burst()
        y = compress(x, SR, release_ms=10.0)
        # Well after the loud section ends, the quiet part passes ~unchanged.
        self.assertAlmostEqual(peak_db(tail(y, 0.15)),
                               peak_db(tail(x, 0.15)), delta=0.5)

    def test_feedback_differs_from_feedforward_and_is_stable(self):
        x = sine(amp=0.8)
        ff = compress(x, SR, topology="feedforward")
        fb = compress(x, SR, topology="feedback")
        self.assertTrue(all(math.isfinite(s) for s in fb))
        diff = max(abs(a - b) for a, b in zip(ff, fb))
        self.assertGreater(diff, 1e-6)

    def test_rms_detector_reduces_less_than_peak(self):
        # RMS of a sine reads ~3 dB below its peak -> less overshoot ->
        # less gain reduction -> louder output.
        x = sine(amp=0.5, dur=0.5)
        y_peak = compress(x, SR, detector="peak")
        y_rms = compress(x, SR, detector="rms")
        self.assertGreater(peak_db(tail(y_rms)), peak_db(tail(y_peak)))


class TestLookahead(unittest.TestCase):
    def test_delay_mode_is_time_aligned_unity_below_threshold(self):
        x = sine(amp=amplitude_from_db(-40.0))
        d = int(round(SR * 5.0 / 1000.0))
        y = compress(x, SR, lookahead="delay", lookahead_ms=5.0)
        self.assertEqual(len(y), len(x))
        pairs = zip(x[:-d], y[d:])          # y is x delayed by d, gain 1
        self.assertLess(max(abs(a - b) for a, b in pairs), 1e-12)

    def test_true_lookahead_holds_the_ceiling(self):
        x = burst(loud_db=-3.0)
        ceiling = -10.0
        y = compress(x, SR, threshold_db=ceiling, ratio=math.inf,
                     knee="hard", knee_db=0.0, ballistics="none",
                     lookahead="true", lookahead_ms=5.0)
        self.assertLessEqual(peak_db(y), ceiling + 0.02)

    def test_no_lookahead_with_slow_attack_overshoots(self):
        # The contrast case: the same limiter without lookahead lets the
        # transient poke through while the attack catches up.
        x = burst(loud_db=-3.0)
        ceiling = -10.0
        y = compress(x, SR, threshold_db=ceiling, ratio=math.inf,
                     knee="hard", knee_db=0.0, ballistics="fixed",
                     attack_ms=5.0, lookahead="none")
        self.assertGreater(peak_db(y), ceiling + 1.0)


class TestMakeupAndValidation(unittest.TestCase):
    def test_auto_makeup_is_louder_than_none(self):
        x = sine(amp=0.5, dur=0.5)
        manual = compress(x, SR, makeup="manual", makeup_db=0.0)
        auto = compress(x, SR, makeup="auto")
        self.assertGreater(peak_db(tail(auto)), peak_db(tail(manual)))

    def test_unknown_option_raises_with_choices(self):
        with self.assertRaises(ValueError) as ctx:
            compress([0.0], SR, knee="bezier")
        self.assertIn("choose from", str(ctx.exception))

    def test_feedback_plus_lookahead_raises(self):
        for la in ("delay", "true"):
            with self.assertRaises(ValueError):
                compress([0.0], SR, topology="feedback", lookahead=la)


class TestPresets(unittest.TestCase):
    def test_all_presets_differ_pairwise(self):
        # The decision map's granularity claim, as an assertion: on the same
        # program material, every pair of reference paths sounds different.
        x = burst()
        outputs = {name: compress(x, SR, **preset)
                   for name, preset in PRESETS.items()}
        names = sorted(outputs)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                diff = max(abs(p - q)
                           for p, q in zip(outputs[a], outputs[b]))
                self.assertGreater(diff, 1e-4, f"{a} vs {b}")


if __name__ == "__main__":
    unittest.main()
