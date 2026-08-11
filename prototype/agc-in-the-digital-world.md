# Automatic Gain Control (AGC) in the digital world

An appendix to [Automatic Gain Control](agc.md), collecting where the function turns up
in digital systems and under what names. The chapter itself covers the effect; this page
covers the field around it.

## Where is AGC?

AGC is less common as a named audio effect than compression or limiting. The function
has not disappeared. It splits between offline systems and real-time systems, and in
music audio neither half is called AGC. Which half applies depends on whether the entire
signal is available for analysis.

For an audio file, there is usually no need for a feedback loop. The level of the entire
signal can be measured before processing, and a fixed gain can then be applied. Loudness
normalization systems such as ITU-R BS.1770 and EBU R128 work this way. There is no
attack or release because the processor does not have to make decisions as the signal
arrives. Those systems measure in LUFS, a perceptual loudness scale that the book defers
along with psychoacoustics generally. The chapters stay in objective signal level, dBFS,
and [Status & scope](status.md) records the deferral.

Real-time systems do not have that advantage. When the future of the signal is unknown,
some form of automatic level control is still useful. It appears in several places:

- Telephony and VoIP. ITU-T G.169 specifies automatic level control (ALC) for digital
  network equipment, and its scope explicitly excludes analog-domain devices. It is a
  standard for AGC as a digital design. WebRTC's AGC2 is an open-source implementation
  of digital automatic gain control.
- Hearing aids. The terminology includes wide-dynamic-range compression, AGC-i
  (input-controlled), and AGC-o (output-controlled). These systems use the same basic
  idea of measuring a changing input and automatically adjusting gain.
- Music production and broadcasting. Similar processing is usually called gain riding,
  leveling, or loudness processing rather than AGC.
- Radio and communications. AGC remains common terminology in software-defined radio
  (SDR) and other communications systems.

The name changes between fields, but the basic control structure is familiar: measure
the signal level, compare it with the desired level, and adjust the gain.

## Why AGC is uncommon in music-DSP texts

Music-DSP texts usually organize dynamics processing around compressors, limiters,
expanders, and gates. AGC can be built from much of the same machinery: a level
detector, a gain calculation, and smoothing to control how quickly that gain changes.

That is the approach used in this book. AGC is treated as another use of the
level-following machinery rather than as a completely separate class of effect. What
separates it from a compressor built from the same parts is the configuration. In the
Woodgate and IEC 60268-8 taxonomy the loop watches its own output and the release runs
to a second or more, and the [AGC chapter](agc.md) sets the release against compression
and limiting on exactly that axis.

## Learn more

- ITU-T Rec. G.169, "Automatic level control devices" (05/2011) —
  [itu.int](https://www.itu.int/rec/T-REC-G.169-201105-I/en). Automatic level control for
  digital network equipment.
- J. M. Kates, *Digital Hearing Aids*, Plural Publishing, 2008 — dynamic-range
  compression chapter. See also Kates, "Principles of Digital Dynamic-Range Compression,"
  *Trends in Amplification* 9(2), 2005 —
  [journals.sagepub.com](https://journals.sagepub.com/doi/10.1177/108471380500900202).
- D. Giannoulis, M. Massberg, J. D. Reiss, "Digital Dynamic Range Compressor Design — A
  Tutorial and Analysis," *JAES* 60(6), 2012 —
  [aes.org](https://www.aes.org/e-lib/browse.cfm?elib=16354).
- Also used elsewhere in this book: Woodgate ISCVE EN 27.1 / IEC 60268-8, WebRTC AGC2,
  and Zölzer, *DAFX*. See [References](references.md).
