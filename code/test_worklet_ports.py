"""Golden tests holding the AudioExplorer JS kernels to the Python they port.

Each interactive sound demo runs its DSP in an AudioWorklet whose kernel is
a hand port of this repository's Python (see
prototype/visualization/lib/tremolo_kernel.js). A port can drift, so each
kernel also runs under Node here, with constant parameters, and its samples
are compared against the Python originals. The tolerance allows only float
noise: the kernel's phase accumulators and Python's closed-form sine agree
to well under a millionth over the tested duration.

Skipped when Node is not installed; the publish workflow's runner has it.

Run from the repo root:  python3 -m unittest discover -s code
"""

import json
import os
import shutil
import subprocess
import unittest

from oscillators import sine_wave, tremolo

HERE = os.path.dirname(__file__)


def run_kernel(runner, *args):
    proc = subprocess.run(
        ["node", os.path.join(HERE, runner)] + [str(a) for a in args],
        capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class TestTremoloKernel(unittest.TestCase):
    def test_matches_python_sample_by_sample(self):
        sr, n = 8000, 4000
        volume, freq, rate, depth = 0.5, 220.0, 5.0, 0.6
        expected = tremolo(sine_wave(freq, n / sr, sr, amp=volume), sr,
                           rate_hz=rate, depth=depth)
        got = run_kernel("run_tremolo_kernel.mjs",
                         sr, n, volume, freq, rate, depth)
        self.assertEqual(len(got), len(expected))
        worst = max(abs(a - b) for a, b in zip(got, expected))
        self.assertLess(worst, 1e-6)

    def test_depth_zero_is_a_plain_sine(self):
        sr, n = 8000, 2000
        got = run_kernel("run_tremolo_kernel.mjs", sr, n, 0.5, 220.0, 5.0, 0.0)
        expected = sine_wave(220.0, n / sr, sr, amp=0.5)
        worst = max(abs(a - b) for a, b in zip(got, expected))
        self.assertLess(worst, 1e-6)
