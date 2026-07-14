# Expanding

> An expander is the mirror image of a compressor: it turns down the quiet parts instead
> of the loud ones, increasing the dynamic range. At extreme settings it becomes a noise
> gate.

*Chapter 6 — companding. The inverse of [Compression](compression.md); a gate is its
extreme setting.*

---

## Intuition

A compressor shrinks the gap between loud and quiet by pulling the loud parts down. An
expander widens the gap by pushing the quiet parts down. Below a chosen threshold, the
quieter the signal, the more it is attenuated.

Typical uses: pushing down hiss, hum, or microphone bleed in the gaps between notes or
words; restoring dynamics to over-compressed material; and, with a steep ratio, gating —
muting a drum microphone except while the drum is struck.

The word companding combines compressing and expanding: the two effects are the same
machinery working in opposite directions around a threshold, and the pair gives this
chapter its name.

## Key parameters

| Parameter | What it controls |
|---|---|
| Threshold | The level (dBFS) below which attenuation begins. |
| Ratio | How hard the signal is pulled down below threshold. 2:1 doubles the dB drop; a very high ratio approaches a gate. |
| Range | The maximum attenuation; how far down the quiet parts may be pushed. |
| Attack | How fast the expander opens (eases off) when the signal rises above threshold (ms). |
| Release | How fast it closes (attenuates) when the signal falls below (ms). |

## How it works

The same detect → map → smooth → apply pipeline, with the transfer function bent the
opposite way from a compressor:

1. Detect the level (peak or RMS).
2. Compare with the threshold. Above it, do nothing. Below it, compute an attenuation
   that grows with the distance below threshold (scaled by the ratio), limited by the
   range.
3. Smooth with the attack (opening) and release (closing) time constants.
4. Apply the gain.

A gate is an expander with a high ratio and a deep range: below the threshold the signal
drops toward silence rather than easing down.

![Transfer curves: unity, 2:1 expansion, and a steep 4:1 curve. Above the −35 dBFS threshold everything is unity; below it the curves bend down, the mirror of a compressor's bend above.](img/expander_transfer.svg)

*The expander's transfer curve bends down below the threshold; on the Compression page's
figure the bend is above it. The steep red curve is close to a gate.*

![Two loud bursts over a −45 dBFS bleed floor. Between bursts the expander pushes the bleed down; it opens fast when a burst arrives and closes slowly after it ends.](img/expander_gate.svg)

*The expander in time (`code/make_figures.py`, using this page's implementation). The
output is bold where the expander is attenuating: the quiet stretches, exactly the
sections a compressor ignores.*

## Pseudocode

```text
for each sample x:
    level   = dBFS(|x|)
    under   = threshold - level                  # how far BELOW threshold
    target  = -under * (ratio - 1)  if under > 0 else 0
    target  = max(target, range)                 # don't exceed the range
    gain    = smooth(gain, target, attack, release)
    y = x * dB_to_linear(gain)
```

## Reference implementation (Python)

```python
import math

def expand(x, sr, threshold_db=-40.0, ratio=2.0, range_db=-40.0,
           attack_ms=5.0, release_ms=100.0):
    """Feed-forward downward expander — pure standard library, no dependencies.

    Below threshold_db it attenuates, increasing dynamic range. A high ratio
    with a deep range_db turns it into a noise gate.

    x:  list of mono samples in [-1, 1]
    sr: sample rate (Hz)
    Returns a new list of samples.
    """
    atk = math.exp(-1.0 / (sr * attack_ms  / 1000.0))
    rel = math.exp(-1.0 / (sr * release_ms / 1000.0))
    eps = 1e-9

    y = []
    env_db = 0.0     # smoothed gain, in dB (<= 0)
    for sample in x:
        level_db = 20.0 * math.log10(abs(sample) + eps)
        under = threshold_db - level_db                 # positive when below threshold
        target = -under * (ratio - 1.0) if under > 0.0 else 0.0
        target = max(target, range_db)                  # floor the attenuation
        # open (toward less attenuation) fast; close (toward more) on release
        coeff = atk if target > env_db else rel
        env_db = coeff * env_db + (1.0 - coeff) * target
        y.append(sample * 10.0 ** (env_db / 20.0))
    return y
```

!!! warning "Pitfalls"
    - Chattering. When the level hovers at the threshold, the expander or gate flickers
      open and shut. Production gates add hysteresis (separate open and close thresholds)
      and a hold time.
    - Chopped tails. A release that is too fast swallows reverb tails, breaths, and note
      decays: quiet material that should be kept.
    - Ratio direction. Expansion attenuates below threshold; compression attenuates above
      it. Confusing the two sides is the classic beginner error.

## Related effects

- [Compression](compression.md): the inverse; it tames the loud parts above a threshold.
- Noise gate: an expander with a high ratio and deep range; silence below threshold.
- [Measuring sound](conventions.md) and [Envelopes](envelopes.md): the level detector and
  one-pole follower this effect is built from.

## Learn more

- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley — its `compexp.m` does
  compression and expansion in one expression.
- Reference implementations: [dafx](references.md#dafx), a combined compressor/expander,
  and [sox](references.md#sox), expansion via transfer-curve breakpoints. Context in the
  [References](references.md) appendix.
