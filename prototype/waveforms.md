# Waveforms & envelopes

*Chapter 4. Partially written — the envelope follower below; sines and other waveforms are
not yet written. See [Status & scope](status.md).*

Planned content: sine waves and the other standard waveforms (square, sawtooth, triangle);
oscillators and LFOs; envelopes. The delay and modulation effects of Chapter 6 and the
tremolo of [Chapter 5](tremolo.md) consume the oscillators defined here.

## Following level over time: attack & release

Effects rarely react instantly; an instantaneous gain change distorts. The response is
smoothed with two time constants:

- Attack: how quickly the effect responds when the level rises.
- Release: how quickly it relaxes when the level falls.

The standard tool is a one-pole smoother, also called an exponential follower. A
coefficient derived from a time in milliseconds controls how sluggish it is:

```python
def smoothing_coeff(time_ms, sr):
    """One-pole coefficient for a given time constant at sample rate sr."""
    return math.exp(-1.0 / (sr * time_ms / 1000.0))

def follow(signal, attack_ms, release_ms, sr):
    """Trace a signal's envelope: fast up (attack), slow down (release)."""
    atk = smoothing_coeff(attack_ms, sr)
    rel = smoothing_coeff(release_ms, sr)
    env = 0.0
    out = []
    for s in signal:
        target = abs(s)
        coeff = atk if target > env else rel   # attack when rising, release when falling
        env = coeff * env + (1.0 - coeff) * target
        out.append(env)
    return out
```

The follow pattern (measure, then smooth toward the measurement) is the backbone of every
effect in [Chapter 5](compression.md). The effects differ mainly in what they do with the
smoothed level.

![Rectified samples of a quiet–loud–quiet tone, with the one-pole envelope riding over them: it rises with the burst in about 5 ms and decays after it in about 50 ms.](img/envelope_follower.svg)

*The `follow` function above, run on a quiet–loud–quiet tone (`code/make_figures.py`). The
envelope rises quickly when the burst starts (attack) and decays slowly after it ends
(release). The amplitude axis is linear; this is the one figure in the book not in dB.*

!!! warning "Pitfall"
    Sample rate is part of every time constant. The same `attack_ms` gives a different
    coefficient at 44.1 kHz than at 48 kHz; always pass `sr` through.
