# Limiting

*Voice sample: textbook (Prince register). Prose sections only.*

---

A limiter is a dynamic-range processor that constrains its output to remain at or below a
fixed level, called the ceiling. It is the limiting case of compression: as the ratio of a
compressor tends to infinity, gain reduction above the threshold approaches the full
overshoot, and the output level above the threshold approaches a constant. A limiter is
therefore specified by the same machinery as a compressor, with the ratio fixed at
infinity, the knee hard, and the time constants fast.

Limiters serve two purposes. The first is protection. Digital systems clip at 0 dBFS, and
converters, transmitters, and storage formats each impose a maximum level; a limiter placed
before such a stage guarantees that the maximum is not exceeded. The second is loudness. A
signal whose peaks are constrained can be raised in overall level without clipping, which
increases loudness at the cost of dynamic range. Moderate use is standard mastering
practice; heavy use degrades the material.

The limiter should be distinguished from AGC, treated in Chapter 1. Both hold the output
level approximately constant above a threshold, and the two are indistinguishable on a
steady-state transfer curve. They differ in their time constants. AGC uses release times of
one second or more and aims to be perceptually transparent; a limiter uses release times of
milliseconds and audibly reshapes transients. Following Woodgate, the distinction is one of
control-loop speed, not of the static characteristic.

## Mechanism

The limiter follows the standard four-stage pipeline of this chapter.

1. Detection. The level detector measures peak level per sample. Peak detection is used in
   preference to RMS because the quantity to be constrained is the instantaneous maximum,
   not the average energy.
2. Gain computation. Let the detected level be L dBFS and the ceiling be C dBFS. For
   L ≤ C the gain is 0 dB. For L > C the gain reduction equals the full overshoot,
   L − C, so that the output level equals C. This is the infinite-ratio transfer function.
3. Smoothing. The gain signal is smoothed by the usual one-pole ballistics with a fast
   attack, typically under one millisecond, and a release chosen for the material.
4. Application. The smoothed gain is applied to the signal.

## Practical considerations

Three limitations of the basic design are important in practice.

First, a feed-forward limiter without lookahead reacts only after a transient has begun,
so brief overshoots pass through during the attack time. Practical brick-wall limiters
delay the audio path by a few milliseconds and compute the gain from the undelayed
detector, so that full gain reduction is in place when the transient reaches the output.
The cost is latency equal to the lookahead time.

Second, constraining sample values does not constrain the reconstructed waveform. The
continuous signal produced by a digital-to-analog converter can exceed the level of every
individual sample between sample instants. These inter-sample peaks motivate true-peak
measurement, in which the signal is oversampled before peak detection; the measurement is
standardized in ITU-R BS.1770. A limiter that enforces a sample-peak ceiling of −1 dBFS
does not, in general, enforce a true-peak ceiling of −1 dBTP.

Third, the release time bounds the audible artifacts. Release times comparable to the
period of low-frequency content cause the gain to track individual cycles, producing
harmonic distortion; long release times cause audible pumping after each peak. The ceiling
is a specification, but the release is a compromise, and it dominates the perceived quality
of a limiter.
