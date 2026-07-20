# Reverb

> Reverb recreates the sound of a space. A room returns thousands of echoes too dense to
> hear separately, and the ear reads their decay as the size and character of the space.

*Chapter 7 — delay and modulation. Many delay lines at once, with fixed delays.*

---

## Intuition

A hand clap in a room comes back from every wall, then from every wall again, and the
reflections multiply until they blur into a smooth decaying wash. One [echo](delay-modulation.md)
line cannot imitate that, because its repeats stay evenly spaced and countable. A
reverberator needs echo density that grows over time, and it needs the density without
adding a metallic ring of its own.

The classic construction is Schroeder's, and it solves the problem in two stages. A bank
of feedback [comb filters](delay-modulation.md) running in parallel supplies the decay,
with delay lengths spread and non-multiple so their echo patterns interleave. A pair of
allpass stages in series then smears each echo into a cluster, multiplying the density
while leaving the overall level of every frequency unchanged.

## Key parameters

| Parameter | What it controls |
|---|---|
| Decay | The comb feedback factor. Higher values ring longer, imitating a larger or more reflective room. |
| Mix | The balance of dry signal and reverberated signal, read as distance to the source. |

## How it works

The comb stage is the [echo](delay-modulation.md) equation with the output taken wet, and
the allpass stage pairs a feedforward path with a feedback path so the two cancel in
level but not in time:

$$
\text{comb:} \quad y[n] = x[n] + g \cdot y[n-D]
$$

$$
\text{allpass:} \quad y[n] = -g \cdot x[n] + x[n-D] + g \cdot y[n-D]
$$

```python
--8<-- "code/delays.py:combs"
```

Four combs in parallel, then two allpasses in series:

```python
--8<-- "code/delays.py:reverb"
```

The delay values are Schroeder's, chosen so that no comb's repeats line up with
another's. The allpass test in `code/test_delays.py` checks the flat-level claim: an
impulse through an allpass keeps its energy while spreading in time.

!!! warning "Pitfalls"
    - Related delay lengths ring. If the comb delays share factors, their repeats
      reinforce at common periods and the tail turns metallic. Spread the lengths.
    - Combs color the sound. Each comb boosts and cuts a regular series of frequencies,
      which is why the allpass stages, which do not, carry the density work.
    - This is a teaching reverberator. Production designs add damping so high frequencies
      decay faster, as they do in air, along with early-reflection models, modulation
      inside the tail, and stereo decorrelation.

## Related effects

- [Echo](delay-modulation.md): one countable repeat pattern. Reverb is what density makes
  of it.
- [Chorus](chorus.md): one moving delay against the dry signal, where reverb uses many
  fixed ones.

## Learn more

- M. R. Schroeder, "Natural Sounding Artificial Reverberation," Journal of the Audio
  Engineering Society, 1962 — the design this page implements.
- Julius O. Smith III, *Physical Audio Signal Processing*,
  [ccrma.stanford.edu/~jos/pasp](https://ccrma.stanford.edu/~jos/pasp/) — Schroeder
  reverberators, Freeverb, and their descendants.
- Freeverb (Jezar at Dreampoint) — the widely ported open reverberator; an STK
  implementation appears in the [References](references.md) appendix's source family.
