/* The waveform explorer's DSP kernel: a direct port of the book's Python.
 *
 * The oscillator pattern and the shape functions come from
 * code/oscillators.py (the Chapter 4 page listing), plus
 * reverse_sawtooth_shape from the same file. The shapes are the naive
 * versions on purpose: at high frequencies the square and sawtooth alias
 * audibly, which is a fold-back the chapter describes. Nothing here
 * touches Web Audio, so the same module runs under Node, and
 * code/test_worklet_ports.py compares every shape against the Python
 * originals sample by sample.
 */

function sineShape(phase) {
  return Math.sin(2.0 * Math.PI * phase);
}

function squareShape(phase) {
  return phase < 0.5 ? 1.0 : -1.0;
}

function sawtoothShape(phase) {
  return 2.0 * phase - 1.0;
}

function reverseSawtoothShape(phase) {
  return 1.0 - 2.0 * phase;
}

function triangleShape(phase) {
  return phase < 0.5 ? 4.0 * phase - 1.0 : 3.0 - 4.0 * phase;
}

/* Index order matches the explorer's selector. */
export const SHAPES = [sineShape, squareShape, sawtoothShape,
                       reverseSawtoothShape, triangleShape];

/* next() returns a bare number: a per-sample allocation on the audio
 * thread becomes a steady rhythm of garbage-collection pauses, audible
 * as a chirp (see lib/explorer_processor_base.js). */
export function createOscillator(sr) {
  let phase = 0.0;      // in [0, 1), the Chapter 4 phase accumulator
  return function next(p) {
    const sample = p.volume * SHAPES[p.shape | 0](phase);
    phase += p.frequency / sr;
    if (phase >= 1.0) phase -= 1.0;
    return sample;
  };
}
