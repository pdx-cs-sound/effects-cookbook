# Limiting

*Voice sample: essayist-engineer (lcamtuf register). Prose sections only.*

---

Digital audio has a number that must not be exceeded. A sample is a float between −1.0 and
+1.0, and there is no such thing as 1.2: whatever the waveform wanted to do up there gets
flattened into a plateau, and the result sounds less like music and more like the music
being torn. Every recording chain therefore ends with the same problem. Somewhere near the
output, something has to make sure the signal stays under the limit, and it has to work on
the worst peak of the worst transient, not on average.

That something is a limiter. The idea is easiest to reach by way of the compressor from the
previous chapter: a compressor turns down loud passages by a ratio, so a 4:1 unit shrinks
4 dB of overshoot to 1 dB. Now imagine negotiating that ratio upward until the compressor
stops negotiating. At infinity, any overshoot at all gets removed completely, and the
output simply cannot pass the ceiling. Marketing calls this a brick-wall limiter, and for
once the marketing term is accurate.

Limiters get used for two reasons, one respectable and one less so. The respectable reason
is safety: set the ceiling just under 0 dBFS and clipping becomes impossible, which is why
there is a limiter in front of practically every broadcast transmitter on earth. The less
respectable reason is that once the peaks are clamped, you can push everything under them
upward, and the track gets louder. Do this tastefully and the master sounds finished. Do it
competitively and you get the loudness war, which spent roughly two decades proving that a
waveform can be shaped like a brick and sell anyway.

One family note before the mechanism. AGC, back in Chapter 1, also holds its output flat;
plot both on a steady-state transfer curve and you get the same line. The entire difference
lives in the time domain. AGC drifts toward its target over seconds, gently enough that you
shouldn't notice it working. A limiter slams the gain down in under a millisecond, and
being noticed is part of the job.

## How it works

The pipeline is the one every effect in this chapter shares: measure the level, compare it
to the threshold, smooth the correction, apply it. A limiter measures peaks, because peaks
are the thing it exists to catch (an averaging detector would cheerfully report that the
signal was fine, on average, while the tweeter died). Below the ceiling it does nothing.
Above the ceiling the gain reduction equals the entire overshoot, so the output lands on
the ceiling exactly. The gain change is then smoothed with a very fast attack and a release
measured in tens of milliseconds, and applied to the signal.

## Where it goes wrong

The basic design has three failure modes worth knowing about.

The first is reaction time. A feed-forward limiter notices a peak only once the peak has
started, so the leading edge of a transient slips through while the attack catches up. The
fix is lookahead: delay the audio by a few milliseconds, compute the gain from the
undelayed copy, and the reduction is already in place when the transient arrives at the
output. You pay for the guarantee with latency, which is why live rigs and mastering
suites configure this differently.

The second is subtler. You can keep every sample at or below the ceiling and still clip
the listener's DAC, because the reconstructed waveform between samples can swing higher
than any sample does. A signal can be perfectly legal at each sample instant and still ask
the converter for more than full scale a microsecond later. These inter-sample peaks are
why serious limiters oversample and enforce a true-peak ceiling; ITU-R BS.1770 defines
the measurement.

The third is the release knob. Too fast, and the gain tracks individual cycles of the bass
and distorts them. Too slow, and every drum hit drags the whole mix down with it and lets
it back up audibly, an effect called pumping. The ceiling is arithmetic; the release is
taste. Two limiters with identical specifications can sound very different, and this knob
is usually the reason.
