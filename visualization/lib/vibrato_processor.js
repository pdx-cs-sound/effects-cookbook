/* The vibrato explorer's AudioWorklet processor: the kernel plus the
 * shared base class. See lib/audio_explorer.js for the harness side. */

import {ExplorerProcessor} from "./explorer_processor_base.js";
import {createVibrato} from "./vibrato_kernel.js";

class VibratoProcessor extends ExplorerProcessor {
  constructor(options) {
    super(options);
    this.next = createVibrato(sampleRate);
  }

  generate(p) {
    return this.next(p);
  }
}

registerProcessor("vibrato-processor", VibratoProcessor);
