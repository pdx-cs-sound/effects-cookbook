/* The AudioWorklet side of an AudioExplorer (see lib/audio_explorer.js).
 *
 * A concrete explorer extends ExplorerProcessor and supplies generate(),
 * usually one call into a kernel ported from the book's Python. The base
 * class owns the plumbing every explorer shares: receiving parameter
 * changes, smoothing them so a moving slider cannot click, clamping the
 * output to full scale, and posting per-block min/max columns for the
 * harness's scope view.
 *
 * The smoothing is a deliberate deviation from the book's code: the
 * Python applies a parameter change instantly, which is fine offline and
 * clicks audibly under a live slider. Roughly 5 ms one-pole smoothing
 * removes the click without changing anything a page teaches.
 */

export class ExplorerProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const params = (options.processorOptions || {}).params || {};
    this.targets = {...params};
    this.smoothed = {...params};
    this.alive = true;
    this.k = 1.0 - Math.exp(-1.0 / (0.005 * sampleRate));
    this.port.onmessage = (e) => {
      if (e.data.type === "param") this.targets[e.data.id] = e.data.value;
      else if (e.data.type === "stop") this.alive = false;
    };
  }

  /* Override: map the smoothed parameter values to one output sample. */
  generate(_params) { return 0.0; }

  /* Override if the scope draws an auxiliary trace (a gain, an envelope). */
  aux() { return 0.0; }

  process(_inputs, outputs) {
    const out = outputs[0][0];
    let min = Infinity;
    let max = -Infinity;
    for (let i = 0; i < out.length; i++) {
      for (const id in this.targets) {
        this.smoothed[id] += (this.targets[id] - this.smoothed[id]) * this.k;
      }
      let s = this.generate(this.smoothed);
      if (s > 1.0) s = 1.0;
      else if (s < -1.0) s = -1.0;
      out[i] = s;
      if (s < min) min = s;
      if (s > max) max = s;
    }
    this.port.postMessage({min, max, aux: this.aux()});
    return this.alive;
  }
}
