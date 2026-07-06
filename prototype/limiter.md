# Limiting

> A **limiter** is a compressor turned up to the extreme: an effectively *infinite* ratio plus a
> fast reaction, so the signal is never allowed to exceed a set **ceiling**. Its job is a
> guarantee — "nothing gets past this level."

*Chapter 2 — Companding. The fast, output-flattening end of [Compression](compression.md);
contrast with the slow, transparent [AGC](agc.md).*

---

## Intuition — what & why

A compressor *leans* on signals above the threshold; a limiter puts up a **brick wall**. Push
as hard as you like — the output simply will not cross the ceiling. Because it has to catch
fast transients, it reacts almost instantly.

**Why you'd use it:** stop a signal from clipping; set a safe maximum before a recording or
broadcast stage; or (the loudness-war use) clamp the peaks so you can raise everything else and
make a track feel louder.

Where it sits among its cousins: a limiter holds the output roughly constant above a threshold —
just like [AGC](agc.md) — but with a **fast** release of milliseconds, where AGC is seconds. And
it's a [compressor](compression.md) with the ratio taken to ∞:1.

## Key parameters

| Parameter | What it controls |
|---|---|
| **Ceiling** | The level (dBFS) the output must never exceed. |
| **Release** | How fast it lets go once the signal drops back below the ceiling (ms). |
| **Attack / lookahead** | How it catches a peak — near-instant attack, or a short lookahead delay so the reduction is already in place when the peak lands. |
| **Knee** | Usually **hard** — the whole point is a firm ceiling. |

## How it works

A limiter is the same detect → map → smooth → apply pipeline as a compressor, with the transfer
function set so that **any** level above the ceiling maps straight back down to it:

1. **Detect** the peak level (limiters are almost always peak, not RMS — they protect against
   peaks).
2. **Compare to the ceiling.** Below it → leave alone. Above it → the gain reduction is exactly
   the overshoot, so the output lands on the ceiling (an ∞:1 ratio).
3. **Smooth** with a very fast attack and a chosen release.
4. **Apply** the gain.

![Transfer curves: unity, a 4:1 compressor, and the limiter's flat wall at a −10 dBFS ceiling.](img/limiter_transfer.svg)

*The limiter's transfer curve next to a 4:1 compressor at the same corner: the compressor
leans, the limiter walls. Same figure grammar as the Compression page — the red ∞:1 curve
there is this page's subject.*

![A quiet–loud–quiet tone through the limiter, with and without lookahead. Without lookahead the output overshoots the ceiling while the attack catches up; with 6 ms of true lookahead it never crosses, at the cost of a 6 ms delay.](img/limiter_lookahead.svg)

*Both traces come from running this book's configurable compressor (`code/make_figures.py`)
at ∞:1. Without lookahead, the burst's leading edge pokes past the ceiling while the 2 ms
attack catches up. With true lookahead the gain is pre-armed and nothing crosses — and the
output arrives 6 ms late, which is the price.*

## Pseudocode

```text
for each sample x:
    level   = dBFS(|x|)                       # peak detector
    over    = level - ceiling
    target  = -over  if over > 0 else 0       # infinite ratio: clamp to the ceiling
    gain    = smooth(gain, target, attack, release)   # very fast attack
    y = x * dB_to_linear(gain)
```

## Reference implementation (Python)

```python
import math

def limit(x, sr, ceiling_db=-1.0, attack_ms=1.0, release_ms=50.0):
    """Feed-forward peak limiter — pure standard library, no dependencies.

    Holds the output at or below ceiling_db. It is a compressor with an
    infinite ratio (any overshoot is removed) and a very fast attack.

    x:  list of mono samples in [-1, 1]
    sr: sample rate (Hz)
    Returns a new list of samples.
    """
    atk = math.exp(-1.0 / (sr * attack_ms  / 1000.0))
    rel = math.exp(-1.0 / (sr * release_ms / 1000.0))
    eps = 1e-9

    y = []
    env_db = 0.0     # smoothed gain reduction, in dB (<= 0)
    for sample in x:
        level_db = 20.0 * math.log10(abs(sample) + eps)
        over = level_db - ceiling_db
        target = -over if over > 0.0 else 0.0     # infinite ratio
        coeff = atk if target < env_db else rel   # attack when clamping harder
        env_db = coeff * env_db + (1.0 - coeff) * target
        y.append(sample * 10.0 ** (env_db / 20.0))
    return y
```

!!! warning "Pitfalls"
    - **Overshoot without lookahead.** A pure feed-forward limiter reacts *after* a peak begins,
      so a fast transient can briefly poke through. True "brick-wall" limiters add a short
      **lookahead** so full reduction is in place the instant the peak arrives.
    - **Inter-sample (true) peaks.** A signal limited to −1 dBFS *in samples* can still exceed
      that between samples after reconstruction. Real limiters oversample and limit to
      **true-peak (dBTP)** — see ITU-R BS.1770.
    - **Distortion vs. pumping.** Too fast a release distorts low frequencies; too slow audibly
      pumps. The ceiling is firm, but the *release* is still a taste decision.
    - **Loudness-war overuse.** Heavy limiting flattens all the life out of a track.

## Related effects

- **[Compression](compression.md)** — the finite-ratio version; a limiter is the ∞:1 extreme.
- **[Automatic Gain Control](agc.md)** — also holds the output flat, but slowly and transparently.
- **Clipping** — the crude alternative: just chop the peaks (cheap, but adds harsh distortion).

## Learn more

- Udo Zölzer (ed.), **DAFX: Digital Audio Effects**, 2nd ed., Wiley.
- **ITU-R BS.1770** — true-peak (dBTP) measurement, the reason real limiters oversample.
- Reference implementations in `thirdparty/compare/`: **audacity** (a true look-ahead limiter),
  **sox** `compand` (limiting via a steep transfer curve).
