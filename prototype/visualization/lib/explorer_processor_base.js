/* The AudioWorklet side of an AudioExplorer (see lib/audio_explorer.js).
 *
 * A concrete explorer extends ExplorerProcessor and supplies generate(),
 * usually one call into a kernel ported from the book's Python. The base
 * class owns the plumbing every explorer shares: receiving parameter
 * changes, smoothing them so a moving slider cannot click, clamping the
 * output to full scale, and posting scope data for the harness's view.
 *
 * The smoothing is a deliberate deviation from the book's code: the
 * Python applies a parameter change instantly, which is fine offline and
 * clicks audibly under a live slider. Roughly 5 ms one-pole smoothing
 * removes the click without changing anything a page teaches.
 *
 * Everything here avoids allocating on the audio thread in steady state.
 * The worklet's JavaScript heap is collected on the rendering thread, so
 * a steady allocation rate becomes a steady rhythm of collection pauses:
 * a few dropouts per second, audible as a chirp riding on high tones in
 * every browser engine. Hence the rules below: kernels return bare
 * numbers rather than objects, scope data is packed into typed arrays,
 * batches are posted every BATCH_BLOCKS quanta with their buffers
 * transferred rather than copied, and the harness sends the buffers back
 * to be reused instead of leaving them for the collector.
 */

const BATCH_BLOCKS = 8;   // 8 x 128 samples: one message per ~21 ms

export class ExplorerProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const po = options.processorOptions || {};
    const params = po.params || {};
    this.targets = {...params};
    this.smoothed = {...params};
    this.ids = Object.keys(params);
    this.discrete = new Set(po.discrete || []);
    this.postSamples = !!po.postSamples;
    this.pool = [];           // recycled ArrayBuffers, returned by the harness
    this.cols = new Float32Array(BATCH_BLOCKS * 3);   // min, max, aux triples
    this.block = 0;
    this.samples = this.postSamples
      ? new Float32Array(BATCH_BLOCKS * 128) : null;
    this.fill = 0;
    this.alive = true;
    this.k = 1.0 - Math.exp(-1.0 / (0.005 * sampleRate));
    this.port.onmessage = (e) => {
      const d = e.data;
      if (d.type === "param") this.targets[d.id] = d.value;
      else if (d.type === "stop") this.alive = false;
      else if (d.type === "recycle") {
        for (const b of d.buffers) this.pool.push(b);
      }
    };
  }

  /* Override: map the smoothed parameter values to one output sample.
   * Must return a number and must not allocate; see the header comment. */
  generate(_params) { return 0.0; }

  /* Override if the scope draws an auxiliary trace (a gain, an envelope). */
  aux() { return 0.0; }

  takeBuffer(length) {
    for (let i = 0; i < this.pool.length; i++) {
      const b = this.pool[i];
      if (b.byteLength === length * 4) {
        this.pool[i] = this.pool[this.pool.length - 1];
        this.pool.pop();
        return new Float32Array(b);
      }
    }
    return new Float32Array(length);
  }

  process(_inputs, outputs) {
    const out = outputs[0][0];
    const ids = this.ids;
    let min = Infinity;
    let max = -Infinity;
    for (let i = 0; i < out.length; i++) {
      for (let j = 0; j < ids.length; j++) {
        const id = ids[j];
        if (this.discrete.has(id)) {
          this.smoothed[id] = this.targets[id];
        } else {
          this.smoothed[id] += (this.targets[id] - this.smoothed[id]) * this.k;
        }
      }
      let s = this.generate(this.smoothed);
      if (s > 1.0) s = 1.0;
      else if (s < -1.0) s = -1.0;
      out[i] = s;
      if (s < min) min = s;
      if (s > max) max = s;
    }
    const base = this.block * 3;
    this.cols[base] = min;
    this.cols[base + 1] = max;
    this.cols[base + 2] = this.aux();
    if (this.samples) {
      this.samples.set(out, this.fill);
      this.fill += out.length;
    }
    this.block += 1;
    if (this.block >= BATCH_BLOCKS) {
      const msg = {columns: this.cols};
      const transfer = [this.cols.buffer];
      if (this.samples) {
        msg.samples = this.samples;
        transfer.push(this.samples.buffer);
      }
      this.port.postMessage(msg, transfer);
      this.cols = this.takeBuffer(BATCH_BLOCKS * 3);
      if (this.postSamples) {
        this.samples = this.takeBuffer(BATCH_BLOCKS * 128);
        this.fill = 0;
      }
      this.block = 0;
    }
    return this.alive;
  }
}
