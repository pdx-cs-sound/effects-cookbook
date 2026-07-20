/* The tremolo explorer's AudioWorklet processor: the kernel plus the
 * shared base class. See lib/audio_explorer.js for the harness side. */

import {ExplorerProcessor} from "./explorer_processor_base.js";
import {createTremolo} from "./tremolo_kernel.js";

class TremoloProcessor extends ExplorerProcessor {
  constructor(options) {
    super(options);
    this.next = createTremolo(sampleRate);
  }

  generate(p) {
    return this.next(p);
  }

  aux() { return this.next.gain; }
}

registerProcessor("tremolo-processor", TremoloProcessor);
