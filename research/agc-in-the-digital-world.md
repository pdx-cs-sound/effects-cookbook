# Where AGC lives in the digital world

*2026-07-27. Closes the "validate additional AGC references" action item from the
2026-07-13 AGC rework. Prompted by Ed's search finding mostly product specs, FPGA/SDR
material, and analog device descriptions.*

## The finding

Searching for "digital AGC" in audio turns up little because the term migrated rather
than the function. Digital audio split AGC's job in two, and neither half kept the name.

**1. Offline loudness normalization absorbed the transparent-leveling job.**
An analog AGC exists because the future of the signal is unknown: the circuit must react
as the signal arrives. A file has no unknown future. Measure the whole program's
loudness once, apply one static gain, and the job AGC was invented for is done with no
control loop, no attack or release, and no pumping. That is what ITU-R BS.1770 loudness
measurement and EBU R128 / streaming-platform normalization do, and it is a genuinely
digital-native solution with no analog counterpart. This is why the music/mastering
world stopped writing about AGC: their version of it is not a dynamics effect anymore.
(Connects to the book's deferred LUFS/loudness scope.)

**2. Real-time AGC survives by other names, in domains where the future stays unknown.**
- *Telephony and VoIP*: ITU-T G.169 "Automatic level control devices" (05/2011) covers
  ALC for digital-network equipment and explicitly excludes analogue-domain devices —
  a fully digital AGC standard. WebRTC's AGC2 (already in the book's references) is the
  open-source implementation of record.
- *Hearing aids*: a large, rigorous digital literature under the names wide-dynamic-range
  compression, AGC-i (input-controlled), and AGC-o (output-controlled). Kates is the
  standard author.
- *Music production*: the same function is sold as gain riding, vocal riders, and
  levelers; broadcast chains call it a loudness processor.
- *SDR and communications*: where Ed's search results came from. Genuinely digital but
  framed for RF (the `sile/dagc` Rust crate follows an SDR-lineage paper,
  "Design and implementation of a new digital automatic gain control").

## Why music-DSP texts are thin on AGC by name

The pro-audio literature (Zölzer's DAFX; Giannoulis/Massberg/Reiss's compressor
tutorial) treats compressor, limiter, expander, and gate as the canonical dynamics
family, with AGC at most a configuration of them: high loop gain and slow release,
exactly the Woodgate/IEC 60268-8 framing the book already adopted. The book's choice to
teach AGC as a goal realized by the follower machinery, rather than as a distinct
algorithm, matches where the field actually is.

## Verified sources (fetch-checked 2026-07-27)

- ITU-T Rec. G.169, "Automatic level control devices" (05/2011) —
  <https://www.itu.int/rec/T-REC-G.169-201105-I/en>. Digital-network ALC; excludes
  analog-domain devices.
- J. M. Kates, *Digital Hearing Aids*, Plural Publishing, 2008 — dynamic-range
  compression chapter. Companion paper: Kates, "Principles of Digital Dynamic-Range
  Compression," *Trends in Amplification* 9(2), 2005 (open access) —
  <https://journals.sagepub.com/doi/10.1177/108471380500900202>. Defines input/output
  AGC in digital hearing-aid terms.
- D. Giannoulis, M. Massberg, J. D. Reiss, "Digital Dynamic Range Compressor Design —
  A Tutorial and Analysis," *JAES* 60(6), 2012 —
  <https://www.aes.org/e-lib/browse.cfm?elib=16354>. The canonical digital dynamics
  tutorial; shows how the field folds AGC-like behavior into compressor design.
- `sile/dagc` — <https://github.com/sile/dagc>. Rust digital AGC; cites
  "Design and implementation of a new digital automatic gain control"
  (<https://hal.univ-lorraine.fr/hal-01397371/document>), SDR lineage.
- Already in the book's references: Woodgate ISCVE EN 27.1 / IEC 60268-8; WebRTC AGC2;
  Zölzer DAFX.

## Possible page impact (Ed's call)

- agc.md "Learn more" could add G.169 and Kates 2005 as the telephony and hearing-aid
  anchors; both are digital-first and citable.
- A short "Where AGC lives today" paragraph on agc.md could preempt the reader's own
  failed search: offline normalization took the transparent job, real-time AGC survives
  in comms and hearing aids, and music tools sell it as riding/leveling. Also a natural
  hook for the deferred-LUFS pointer.
- "Pumping" as an artifact name is worth a sentence on the AGC or compression pitfalls
  when demos exist to make it audible.
