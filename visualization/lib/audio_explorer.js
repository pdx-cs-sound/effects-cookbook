/* AudioExplorer: the shared harness for the cookbook's interactive sound
 * demos.
 *
 * One explorer = this harness + a small AudioWorklet processor whose DSP
 * kernel is a direct port of the book's Python (see lib/tremolo_kernel.js
 * for the pattern; code/test_worklet_ports.py holds each kernel to its
 * Python original). The harness owns everything an explorer needs beyond
 * the DSP: the play/stop gesture the browser requires before audio may
 * start, labeled controls with live readouts, the oscilloscope view, and
 * message plumbing to the worklet.
 *
 * Controls are sliders ({id, label, min, max, step, value, format}, with
 * scale: "log" for ranges the ear hears in octaves) or segmented radio
 * groups ({type: "select", options: [{label, value}]}). Select values are
 * discrete: the worklet applies them instantly instead of smoothing them,
 * since a fractional waveform index means nothing.
 *
 * The scope has two modes. "envelope" (default) draws scope.seconds of
 * per-block min/max columns, the right view when the story is slower than
 * the waveform (a tremolo swell). "cycles" draws a few triggered periods
 * from raw samples, the right view when the story is the shape itself.
 *
 * Plain JavaScript and Canvas, no dependencies. Colors follow the figure
 * conventions in code/make_figures.py: gray input/reference, blue output,
 * amber gain, purple reference levels, mid-tones legible on both themes.
 */

const GRAY = "#888780";
const BLUE = "#378add";
const AMBER = "#d98a00";
const PURPLE = "#7f77dd";

export class AudioExplorer {
  /* config:
   *   mount          element to build the UI inside
   *   processorUrl   worklet module URL (relative to the page)
   *   processorName  name passed to registerProcessor in that module
   *   controls       slider and select descriptors, see above
   *   scope          {mode, seconds, description, gainLabel or null}
   */
  constructor(config) {
    this.config = config;
    this.values = {};
    for (const c of config.controls) this.values[c.id] = c.value;
    this.ctx = null;
    this.node = null;
    this.running = false;
    this.columns = [];        // envelope mode: ring of {min, max, aux}
    this.capacity = 0;
    this.head = 0;
    this.samples = [];        // cycles mode: rolling raw samples
    this.buildUi(config.mount);
    this.drawScope();
  }

  buildUi(mount) {
    const cfg = this.config;
    this.button = document.createElement("button");
    this.button.type = "button";
    this.button.className = "ax-play";
    this.button.textContent = "Play tone";
    this.button.setAttribute("aria-pressed", "false");
    this.button.addEventListener("click", () => this.toggle());
    mount.appendChild(this.button);

    const panel = document.createElement("div");
    panel.className = "ax-controls";
    for (const c of cfg.controls) {
      panel.appendChild(c.type === "select"
        ? this.buildSelect(c) : this.buildSlider(c));
    }
    mount.appendChild(panel);

    this.canvas = document.createElement("canvas");
    this.canvas.className = "ax-scope";
    this.canvas.setAttribute("role", "img");
    this.canvas.setAttribute("aria-label", cfg.scope.description);
    mount.appendChild(this.canvas);

    const legend = document.createElement("p");
    legend.className = "ax-legend";
    const entries = [["output waveform", BLUE, "solid"]];
    if (cfg.scope.gainLabel) entries.push([cfg.scope.gainLabel, AMBER, "solid"]);
    entries.push(["volume setting", GRAY, "dashed"]);
    entries.push(["full scale", PURPLE, "dashed"]);
    for (const [text, color, style] of entries) {
      const swatch = document.createElement("span");
      swatch.className = "ax-swatch";
      swatch.style.borderTop = `2px ${style} ${color}`;
      legend.appendChild(swatch);
      legend.appendChild(document.createTextNode(" " + text + "  "));
    }
    mount.appendChild(legend);
  }

  buildSlider(c) {
    const log = c.scale === "log";
    const toValue = (raw) => log ? 2 ** raw : raw;
    const toRaw = (value) => log ? Math.log2(value) : value;
    const label = document.createElement("label");
    label.className = "ax-control";
    const name = document.createElement("span");
    name.className = "ax-name";
    name.textContent = c.label;
    const input = document.createElement("input");
    input.type = "range";
    input.min = toRaw(c.min);
    input.max = toRaw(c.max);
    // A log slider is continuous: a step grid anchored at log2(min) has
    // no representable values, and the browser flags them as invalid.
    input.step = log ? "any" : c.step;
    input.value = toRaw(c.value);
    const readout = document.createElement("output");
    readout.className = "ax-readout";
    const show = () => { readout.textContent = c.format(this.values[c.id]); };
    input.addEventListener("input", () => {
      this.setParam(c.id, toValue(Number(input.value)));
      show();
    });
    show();
    label.appendChild(name);
    label.appendChild(input);
    label.appendChild(readout);
    return label;
  }

  buildSelect(c) {
    const group = document.createElement("div");
    group.className = "ax-control ax-select";
    const name = document.createElement("span");
    name.className = "ax-name";
    name.id = `ax-name-${c.id}`;
    name.textContent = c.label;
    const options = document.createElement("div");
    options.className = "ax-options";
    options.setAttribute("role", "radiogroup");
    options.setAttribute("aria-labelledby", name.id);
    for (const o of c.options) {
      const label = document.createElement("label");
      label.className = "ax-option";
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = `ax-${c.id}`;
      radio.value = o.value;
      radio.checked = o.value === c.value;
      radio.addEventListener("change", () => {
        if (radio.checked) this.setParam(c.id, Number(radio.value));
      });
      label.appendChild(radio);
      label.appendChild(document.createTextNode(o.label));
      options.appendChild(label);
    }
    group.appendChild(name);
    group.appendChild(options);
    return group;
  }

  setParam(id, value) {
    this.values[id] = value;
    if (this.node) {
      this.node.port.postMessage({type: "param", id, value});
    }
    this.drawScope();
  }

  async toggle() {
    if (this.running) { this.stop(); } else { await this.start(); }
  }

  async start() {
    const cfg = this.config;
    if (!this.ctx) {
      this.ctx = new AudioContext();
      await this.ctx.audioWorklet.addModule(cfg.processorUrl);
      if (cfg.scope.mode !== "cycles") {
        this.capacity = Math.ceil(cfg.scope.seconds * this.ctx.sampleRate / 128);
      }
    }
    await this.ctx.resume();
    this.columns = [];
    this.head = 0;
    this.samples = [];
    this.node = new AudioWorkletNode(this.ctx, cfg.processorName, {
      numberOfInputs: 0,
      processorOptions: {
        params: {...this.values},
        discrete: cfg.controls.filter((c) => c.type === "select")
                              .map((c) => c.id),
        postSamples: cfg.scope.mode === "cycles",
      },
    });
    this.node.port.onmessage = (e) => this.receive(e.data);
    this.node.connect(this.ctx.destination);
    this.running = true;
    this.button.textContent = "Stop";
    this.button.setAttribute("aria-pressed", "true");
    const frame = () => {
      if (!this.running) return;
      this.drawScope();
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  stop() {
    if (this.node) {
      this.node.port.postMessage({type: "stop"});
      this.node.disconnect();
      this.node = null;
    }
    this.running = false;
    this.button.textContent = "Play tone";
    this.button.setAttribute("aria-pressed", "false");
    this.drawScope();       // freeze the last view on screen
  }

  /* Scope data arrives packed (columns as min/max/aux triples, samples
   * as one transferred buffer per batch); the buffers go back to the
   * worklet for reuse, so the audio thread never allocates in steady
   * state. */
  receive(data) {
    const cols = data.columns;
    if (this.config.scope.mode === "cycles") {
      this.samples.push(...data.samples);
      const cap = Math.ceil(this.ctx.sampleRate / 2);
      if (this.samples.length > cap) {
        this.samples.splice(0, this.samples.length - cap);
      }
    } else {
      for (let i = 0; i < cols.length; i += 3) {
        const col = {min: cols[i], max: cols[i + 1], aux: cols[i + 2]};
        if (this.columns.length < this.capacity) {
          this.columns.push(col);
        } else {
          this.columns[this.head] = col;
          this.head = (this.head + 1) % this.capacity;
        }
      }
    }
    if (this.node) {
      const buffers = [cols.buffer];
      if (data.samples) buffers.push(data.samples.buffer);
      this.node.port.postMessage({type: "recycle", buffers}, buffers);
    }
  }

  drawScope() {
    const canvas = this.canvas;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 640;
    const h = canvas.clientHeight || 240;
    if (canvas.width !== w * dpr) { canvas.width = w * dpr; }
    if (canvas.height !== h * dpr) { canvas.height = h * dpr; }
    const g = canvas.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, h);
    const pad = 8;
    const y = (v) => h / 2 - v * (h / 2 - pad);

    g.strokeStyle = GRAY;
    g.globalAlpha = 0.25;
    g.beginPath(); g.moveTo(0, y(0)); g.lineTo(w, y(0)); g.stroke();
    g.globalAlpha = 1.0;

    g.setLineDash([5, 4]);
    g.strokeStyle = PURPLE;
    g.lineWidth = 1;
    for (const v of [1, -1]) {
      g.beginPath(); g.moveTo(0, y(v)); g.lineTo(w, y(v)); g.stroke();
    }
    g.fillStyle = PURPLE;
    g.font = "10px system-ui, sans-serif";
    g.textAlign = "right";
    g.fillText("full scale", w - 4, y(1) + 11);

    const vol = this.values.volume;
    if (vol !== undefined) {
      g.strokeStyle = GRAY;
      for (const v of [vol, -vol]) {
        g.beginPath(); g.moveTo(0, y(v)); g.lineTo(w, y(v)); g.stroke();
      }
    }
    g.setLineDash([]);

    if (this.config.scope.mode === "cycles") {
      this.drawCycles(g, w, y);
    } else {
      this.drawEnvelope(g, w, y);
    }
  }

  drawEnvelope(g, w, y) {
    const n = this.columns.length;
    if (n === 0) return;
    const x = (i) => (i / (this.capacity - 1)) * w;
    g.strokeStyle = BLUE;
    g.globalAlpha = 0.9;
    g.lineWidth = 1;
    g.beginPath();
    for (let i = 0; i < n; i++) {
      const col = this.columns[(this.head + i) % n];
      const xi = x(i);
      g.moveTo(xi, y(col.max));
      g.lineTo(xi, y(col.min) + 0.5);
    }
    g.stroke();
    g.globalAlpha = 1.0;

    if (this.config.scope.gainLabel) {
      g.strokeStyle = AMBER;
      g.lineWidth = 2;
      g.beginPath();
      for (let i = 0; i < n; i++) {
        const col = this.columns[(this.head + i) % n];
        if (i === 0) g.moveTo(x(i), y(col.aux));
        else g.lineTo(x(i), y(col.aux));
      }
      g.stroke();
    }
  }

  /* A few periods of the raw waveform, anchored at a rising zero crossing
   * (an oscilloscope trigger) so the drawing holds still. The crossing
   * falls between two samples, so the anchor keeps its fractional
   * position; snapping it to a whole sample makes the trace jitter
   * sideways by up to a sample, which is a visible fraction of a period
   * at high frequencies. */
  drawCycles(g, w, y) {
    const sr = this.ctx ? this.ctx.sampleRate : 48000;
    const freq = this.values.frequency || 220;
    const win = Math.min(this.samples.length,
                         Math.round(3 * sr / freq));
    if (win < 2) return;
    let start = this.samples.length - win;
    let frac = 0.0;
    const search = Math.min(start, Math.round(sr / freq));
    for (let i = start; i > start - search; i--) {
      const a = this.samples[i - 1];
      const b = this.samples[i];
      if (a <= 0 && b > 0) {
        start = i;
        frac = 1.0 - a / (a - b);    // crossing sits frac before sample i
        break;
      }
    }
    g.strokeStyle = BLUE;
    g.lineWidth = 2;
    g.beginPath();
    for (let i = 0; i < win; i++) {
      const xi = ((i + frac) / (win - 1)) * w;
      const yi = y(this.samples[start + i]);
      if (i === 0) g.moveTo(xi, yi);
      else g.lineTo(xi, yi);
    }
    g.stroke();
  }
}
