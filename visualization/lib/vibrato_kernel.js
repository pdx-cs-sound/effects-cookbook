/* The vibrato explorer's DSP kernel: a direct port of the book's Python.
 *
 * The carrier is the Chapter 4 oscillator pattern with the sine shape, and
 * the effect is vibrato() from code/delays.py: an LFO sweeps a fractional
 * delay, and the sweep shifts the pitch. The ring buffer follows
 * RingBuffer in the same file, reading before writing on every sample, so
 * read(d) returns the value pushed d samples ago.
 *
 * The base delay is held at the book's default rather than exposed as a
 * control: it sets latency, not the sound. Nothing here touches Web Audio,
 * so the same module runs under Node, and code/test_worklet_ports.py
 * compares its output against the Python original sample by sample.
 *
 * next() returns a bare number and reports the current delay through a
 * property on the function: the kernel runs on the audio thread, which
 * must not allocate per sample (see lib/explorer_processor_base.js).
 */

const BASE_MS = 5.0;    // delays.py vibrato(base_ms=5.0)
const MAX_MS = 40.0;    // sized for the widest sweep the controls allow

export function createVibrato(sr) {
  const len = Math.ceil(sr * MAX_MS / 1000.0) + 2;
  const buf = new Float64Array(len);
  let pos = 0;
  let phase = 0.0;      // carrier phase, in [0, 1)
  let lfoPhase = 0.0;   // sweep phase, in [0, 1)

  function read(delay) {
    let i = (pos - delay) % len;
    if (i < 0) i += len;
    return buf[i];
  }

  function next(p) {
    const carrier = p.volume * Math.sin(2.0 * Math.PI * phase);
    const lfo = 0.5 + 0.5 * Math.sin(2.0 * Math.PI * lfoPhase);   // in [0, 1]
    const delayMs = BASE_MS + p.depth * lfo;
    const delay = delayMs * sr / 1000.0;
    const i = Math.floor(delay);
    const frac = delay - i;
    const delayed = (1.0 - frac) * read(i) + frac * read(i + 1);
    buf[pos] = carrier;
    pos = (pos + 1) % len;
    phase += p.frequency / sr;
    if (phase >= 1.0) phase -= 1.0;
    lfoPhase += p.rate / sr;
    if (lfoPhase >= 1.0) lfoPhase -= 1.0;
    next.delayMs = delayMs;
    return delayed;
  }
  next.delayMs = BASE_MS;
  return next;
}
