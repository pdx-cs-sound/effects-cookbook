/* The waveform explorer's AudioWorklet processor: the kernel plus the
 * shared base class. See lib/audio_explorer.js for the harness side. */

import {ExplorerProcessor} from "./explorer_processor_base.js";
import {createOscillator} from "./waveform_kernel.js";

class WaveformProcessor extends ExplorerProcessor {
  constructor(options) {
    super(options);
    this.next = createOscillator(sampleRate);
  }

  generate(p) {
    return this.next(p);
  }
}

registerProcessor("waveform-processor", WaveformProcessor);
