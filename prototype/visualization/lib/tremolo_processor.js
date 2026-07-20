/* The tremolo explorer's AudioWorklet processor: the kernel plus the
 * shared base class. See lib/audio_explorer.js for the harness side. */

import {ExplorerProcessor} from "./explorer_processor_base.js";
import {createTremolo} from "./tremolo_kernel.js";

class TremoloProcessor extends ExplorerProcessor {
  constructor(options) {
    super(options);
    this.next = createTremolo(sampleRate);
    this.lastGain = 1.0;
  }

  generate(p) {
    const r = this.next(p);
    this.lastGain = r.gain;
    return r.sample;
  }

  aux() { return this.lastGain; }
}

registerProcessor("tremolo-processor", TremoloProcessor);
