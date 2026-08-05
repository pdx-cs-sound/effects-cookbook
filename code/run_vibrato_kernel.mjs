// Node runner for the golden test in test_worklet_ports.py: generate
// samples from the vibrato explorer's JS kernel with constant parameters
// and print them as JSON for comparison against the Python original.
//
// Usage: node run_vibrato_kernel.mjs <sr> <n> <volume> <frequency> <rate> <depth>

import {createVibrato} from "../prototype/visualization/lib/vibrato_kernel.js";

const [sr, n, volume, frequency, rate, depth] =
  process.argv.slice(2).map(Number);
const next = createVibrato(sr);
const out = new Array(n);
for (let i = 0; i < n; i++) {
  out[i] = next({volume, frequency, rate, depth});
}
process.stdout.write(JSON.stringify(out));
