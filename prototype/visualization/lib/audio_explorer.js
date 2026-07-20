/* AudioExplorer: the shared harness for the cookbook's interactive sound
 * demos.
 *
 * One explorer = this harness + a small AudioWorklet processor whose DSP
 * kernel is a direct port of the book's Python (see lib/tremolo_kernel.js
 * for the pattern; code/test_worklet_ports.py holds each kernel to its
 * Python original). The harness owns everything an explorer needs beyond
 * the DSP: the play/stop gesture the browser requires before audio may
 * start, labeled sliders with live readouts, the rolling oscilloscope
 * view, and message plumbing to the worklet.
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
   *   controls       [{id, label, min, max, step, value, format}]
   *   scope          {seconds, description, gainLabel or null}
   */
  constructor(config) {
    this.config = config;
    this.values = {};
    for (const c of config.controls) this.values[c.id] = c.value;
    this.ctx = null;
    this.node = null;
    this.running = false;
    this.columns = [];        // ring of {min, max, aux} scope columns
    this.capacity = 0;
    this.head = 0;
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
      const label = document.createElement("label");
      label.className = "ax-control";
      const name = document.createElement("span");
      name.className = "ax-name";
      name.textContent = c.label;
      const input = document.createElement("input");
      input.type = "range";
      input.min = c.min;
      input.max = c.max;
      input.step = c.step;
      input.value = c.value;
      const readout = document.createElement("output");
      readout.className = "ax-readout";
      const show = () => { readout.textContent = c.format(Number(input.value)); };
      input.addEventListener("input", () => {
        this.values[c.id] = Number(input.value);
        show();
        if (this.node) {
          this.node.port.postMessage(
            {type: "param", id: c.id, value: this.values[c.id]});
        }
        this.drawScope();
      });
      show();
      label.appendChild(name);
      label.appendChild(input);
      label.appendChild(readout);
      panel.appendChild(label);
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

  async toggle() {
    if (this.running) { this.stop(); } else { await this.start(); }
  }

  async start() {
    if (!this.ctx) {
      this.ctx = new AudioContext();
      await this.ctx.audioWorklet.addModule(this.config.processorUrl);
      this.capacity = Math.ceil(
        this.config.scope.seconds * this.ctx.sampleRate / 128);
    }
    await this.ctx.resume();
    this.columns = [];
    this.head = 0;
    this.node = new AudioWorkletNode(this.ctx, this.config.processorName, {
      numberOfInputs: 0,
      processorOptions: {params: {...this.values}},
    });
    this.node.port.onmessage = (e) => this.pushColumn(e.data);
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
    this.drawScope();       // freeze the last second on screen
  }

  pushColumn(col) {
    if (this.columns.length < this.capacity) {
      this.columns.push(col);
    } else {
      this.columns[this.head] = col;
      this.head = (this.head + 1) % this.capacity;
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
}
