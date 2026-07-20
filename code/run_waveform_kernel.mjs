// Node runner for the golden test in test_worklet_ports.py: generate
// samples from the waveform explorer's JS kernel with constant parameters
// and print them as JSON for comparison against the Python originals.
//
// Usage: node run_waveform_kernel.mjs <sr> <n> <volume> <frequency> <shape>
// where <shape> indexes SHAPES: 0 sine, 1 square, 2 sawtooth,
// 3 reverse sawtooth, 4 triangle.

import {createOscillator} from "../prototype/visualization/lib/waveform_kernel.js";

const [sr, n, volume, frequency, shape] = process.argv.slice(2).map(Number);
const next = createOscillator(sr);
const out = new Array(n);
for (let i = 0; i < n; i++) {
  out[i] = next({volume, frequency, shape});
}
process.stdout.write(JSON.stringify(out));
