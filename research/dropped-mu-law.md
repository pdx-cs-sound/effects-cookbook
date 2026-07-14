# Dropped: mu-law (from Chapter 3)

Cut 2026-07-13 on meeting feedback: interesting, but it does not quite fit the book.
Archived here in case it returns (a codecs aside, an appendix, or nowhere). The figure
generator function (`fig_mulaw_transfer`) was removed from `code/make_figures.py` in the
same change; git history has both.

Context it needed: it was the fourth link of Chapter 3's chain (bit crush shows the damage
quantization does; mu-law was the classic treatment), and it carried the disambiguation
between codec-sense companding and the level effects. With mu-law gone, "Companding" is
free to be Chapter 6's title.

---

## Mu-law

Mu-law spends a fixed number of levels unevenly, so that quiet samples — where
quantization hurts most — get most of them. Before quantizing, each sample is bent through
a curve that is steep near zero; after storage or transmission, the exact inverse curve
bends it back.

```python
import math

def mu_compress(x, mu=255.0):
    """Bend samples so quiet values use more of the output range."""
    scale = math.log(1.0 + mu)
    return [math.copysign(math.log(1.0 + mu * abs(s)) / scale, s) for s in x]

def mu_expand(y, mu=255.0):
    """The exact inverse of mu_compress."""
    return [math.copysign(((1.0 + mu) ** abs(s) - 1.0) / mu, s) for s in y]
```

(Round trip verified to about 8e-16 worst-case error.)

The mu-law pair at μ = 255: compression before quantizing, expansion after. With μ = 255
and 8 bits, this is the encoding of ITU-T G.711, the standard that carried telephone audio
for decades: 8-bit storage with quiet-signal fidelity closer to 12-bit linear.

This is companding in the codec sense — compress, store, expand — and it shares nothing
but the name's origin with the level effects. The differences: the mu-law pair is
instantaneous and stateless, the two curves are exact inverses so the round trip is
transparent, and the goal is precision, not dynamics.

Pitfall it carried: the two halves must match. Expanding audio that was never compressed,
or playing G.711 bytes as if they were linear samples, applies one half of the pair alone.

Reference: ITU-T Recommendation [G.711](https://www.itu.int/rec/T-REC-G.711) — mu-law and
its European sibling, A-law; free from itu.int.
