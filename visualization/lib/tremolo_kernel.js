/* The tremolo explorer's DSP kernel: a direct port of the book's Python.
 *
 * The carrier is the Chapter 4 oscillator pattern (a phase that climbs
 * from 0 to 1 and wraps) with the sine shape, and the gain is tremolo()
 * from code/oscillators.py. Nothing here touches Web Audio, so the same
 * module runs under Node, and code/test_worklet_ports.py compares its
 * output against the Python originals sample by sample.
 *
 * next() returns a bare number and reports the gain through a property
 * on the function rather than returning an object: the kernel runs on
 * the audio thread, where a per-sample allocation becomes a steady
 * rhythm of garbage-collection pauses, audible as a chirp (see
 * lib/explorer_processor_base.js).
 */

export function createTremolo(sr) {
  let phase = 0.0;      // carrier phase, in [0, 1)
  let lfoPhase = 0.0;   // tremolo LFO phase, in [0, 1)
  function next(p) {
    const carrier = Math.sin(2.0 * Math.PI * phase);
    const m = 0.5 + 0.5 * Math.sin(2.0 * Math.PI * lfoPhase);  // LFO in [0, 1]
    const gain = 1.0 - p.depth * m;
    phase += p.frequency / sr;
    if (phase >= 1.0) phase -= 1.0;
    lfoPhase += p.rate / sr;
    if (lfoPhase >= 1.0) lfoPhase -= 1.0;
    next.gain = gain;
    return p.volume * gain * carrier;
  }
  next.gain = 1.0;
  return next;
}
