# Limiting

*Voice sample: flat (specification register). Prose sections only.*

---

A limiter holds its output at or below a fixed level. The level is called the ceiling.
Input below the ceiling passes through unchanged. Input above the ceiling is reduced to
the ceiling.

A limiter is a compressor with an infinite ratio. A 4:1 compressor reduces 4 dB of
overshoot to 1 dB; as the ratio grows, the output above the threshold approaches a
constant. At an infinite ratio the overshoot is removed completely. The knee is hard and
the time constants are fast. The configuration is sometimes called brick-wall limiting.

Limiting has two uses. The first is protection. Digital audio clips at 0 dBFS, and
converters, transmitters, and storage formats each have a maximum level; a limiter placed
before such a stage keeps the signal below the maximum. The second is loudness. When the
peaks are held down, the overall level can be raised without clipping. This trades dynamic
range for loudness.

AGC, from Chapter 1, also holds its output approximately constant. The two are identical
on a steady-state transfer curve. They differ in release time. AGC releases over one
second or more and aims to be inaudible; a limiter releases in milliseconds and is audible
on transients.

## Mechanism

The pipeline is the same four stages as the other effects in this chapter.

1. Detect the peak level, per sample. Peak detection is used because the quantity being
   constrained is the instantaneous maximum, not the average.
2. Compare with the ceiling. At or below the ceiling, the gain is 0 dB. Above it, the gain
   reduction equals the overshoot, so the output equals the ceiling.
3. Smooth the gain with a fast attack, typically under one millisecond, and a chosen
   release.
4. Apply the gain to the signal.

## Limitations

Without lookahead, a feed-forward limiter reacts after a transient begins, and the leading
edge passes above the ceiling during the attack time. A lookahead limiter delays the audio
by a few milliseconds and computes the gain from the undelayed signal, so the reduction is
in place when the transient reaches the output. The cost is latency equal to the lookahead
time.

Holding every sample at or below the ceiling does not hold the reconstructed waveform
there. The continuous signal a converter produces between samples can exceed the samples.
These inter-sample peaks are measured by oversampling before peak detection; ITU-R BS.1770
defines the measurement (true peak, dBTP). A sample-peak ceiling does not guarantee a
true-peak ceiling.

The release time sets the artifacts. A release comparable to the period of low-frequency
content tracks individual cycles and distorts them. A long release lowers the level
audibly after each peak, called pumping. The ceiling is a specification; the release is
chosen by listening.
