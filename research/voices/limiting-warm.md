# Limiting

*Voice sample: warm teacher (Asimov register). Prose sections only.*

---

A limiter is a machine that keeps a promise. The promise is simple to state: the signal
that comes out will never rise above a chosen level, called the ceiling. Everything else
about the limiter follows from taking that promise seriously.

Let's see how such a promise could be kept. You already know what a compressor does: when
the signal crosses a threshold, the compressor turns it down, but only partway. A 4:1
compressor lets a 4 dB overshoot through as 1 dB. That's a gentle sort of discipline, and
for most purposes it's exactly what you want. But suppose you can't afford gentleness.
Suppose the next stage in the chain clips at some exact level, and one stray peak will
produce an ugly crack in the audio. Partway isn't good enough anymore. You want every
decibel of overshoot removed, not three quarters of it.

So imagine turning the compressor's ratio up. At 10:1, a 4 dB overshoot comes through as
0.4 dB. At 100:1, it's 0.04 dB. Carry the idea to its logical end, an infinite ratio, and
the overshoot vanishes entirely: whatever goes over the ceiling comes out at the ceiling.
That is a limiter. It isn't a new device at all. It's the compressor we already understand,
pushed to its extreme, and made fast enough to catch peaks before they do any harm.

## Why you'd want one

The obvious use is protection. Digital audio has a hard edge at 0 dBFS, and a limiter set
just below that edge guarantees you never hit it. Broadcasters put limiters ahead of their
transmitters for the same reason, and a careful engineer puts one at the end of a recording
chain before an irreplaceable take.

The less innocent use is loudness. If the peaks are clamped down, everything underneath
them can be raised, and the whole track feels louder without ever clipping. Used in
moderation this is a normal part of finishing a record. Used without moderation it flattens
the life out of one, and the industry spent a couple of decades demonstrating that at scale.

It's worth pausing to notice where the limiter sits in the family. AGC, from Chapter 1,
also holds its output level roughly constant; on a steady-state graph the two draw exactly
the same flattened line. The difference is speed. AGC corrects over seconds and tries to be
inaudible. A limiter corrects in milliseconds and doesn't apologize.

## How it works

The pipeline is the same one every effect in this chapter uses: detect, compare, smooth,
apply. The limiter's version goes like this. First, measure the peak level of the incoming
signal; limiters watch peaks, not averages, because peaks are what they're paid to catch.
Second, compare against the ceiling. Below it, do nothing at all. Above it, compute a gain
reduction equal to the entire overshoot, so the output lands exactly on the ceiling; that's
the infinite ratio doing its work. Third, smooth that gain change with a very fast attack
and a release you choose by ear. Fourth, apply the gain.

## The ways it can go wrong

Now for the traps, and there are a few. The first is that a plain feed-forward limiter
reacts to a peak after the peak has begun. However fast the attack, some sliver of
transient gets through before the gain comes down. Real brick-wall limiters solve this by
delaying the audio slightly and computing the gain from the undelayed signal, so the
reduction is already in place when the peak arrives. That trick is called lookahead, and
the price is a few milliseconds of latency.

The second trap is sneakier. You can hold every sample at or below the ceiling and still
clip, because the smooth waveform reconstructed between samples can swing higher than the
samples themselves. These inter-sample peaks are why serious limiters oversample and
measure true peak rather than sample peak; the broadcast standard for this is ITU-R
BS.1770.

The third trap is the release. Make it too fast and the gain follows the shape of low
notes closely enough to distort them. Make it too slow and each loud hit drags the level
down audibly, and the track pumps. The ceiling is not negotiable, but the release is pure
judgment, and it's where limiters earn their reputations.
