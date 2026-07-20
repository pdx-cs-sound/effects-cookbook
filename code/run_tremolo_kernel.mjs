// Node runner for the golden test in test_worklet_ports.py: generate
// samples from the tremolo explorer's JS kernel with constant parameters
// and print them as JSON for comparison against the Python originals.
//
// Usage: node run_tremolo_kernel.mjs <sr> <n> <volume> <frequency> <rate> <depth>

import {createTremolo} from "../prototype/visualization/lib/tremolo_kernel.js";

const [sr, n, volume, frequency, rate, depth] =
  process.argv.slice(2).map(Number);
const next = createTremolo(sr);
const out = new Array(n);
for (let i = 0; i < n; i++) {
  out[i] = next({volume, frequency, rate, depth}).sample;
}
process.stdout.write(JSON.stringify(out));
