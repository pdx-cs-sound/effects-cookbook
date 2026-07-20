# Chorus

> Chorus mixes a slightly delayed, slowly pitch-wobbling copy of a signal with the
> original. The result sounds like more than one performer.

*Chapter 7 — delay and modulation. [Vibrato](vibrato.md) plus a dry mix.*

---

## Intuition

Two singers on the same note are never exactly together. Their timing drifts by
milliseconds and their pitch drifts by cents, and the drift itself is what the ear reads
as two voices rather than one. Chorus manufactures that drift. It takes one signal, makes
a copy through a slowly swept delay line, and mixes the copy back with the original. The
copy is a [vibrato](vibrato.md) voice, and the mix is the whole trick:

```python
--8<-- "code/delays.py:chorus"
```

## Key parameters

| Parameter | What it controls |
|---|---|
| Rate | How fast the copy drifts (Hz). Chorus rates sit well below vibrato rates, near 1 Hz. |
| Depth | How far the copy drifts (ms). |
| Base delay | The average offset of the copy (ms), typically 15 to 30 ms, inside the range the ear fuses. |
| Mix | The balance of original and copy. Equal parts is the classic setting. |

## How it works

1. Run [vibrato](vibrato.md) on the input with a slow rate and a base delay of tens of
   milliseconds.
2. Mix the result with the unprocessed input.

The differences from vibrato are the dry mix and the settings. Vibrato is heard alone, so
its pitch wobble is the point. The chorus copy is heard against the original, so the
wobble becomes beating and shimmer between two voices. Richer choruses run several copies
with different rates and phases, and the same idea at higher depths and shorter delays
becomes flanging.

!!! warning "Pitfalls"
    - The mixed copy interferes with the original. At any instant the pair forms a comb
      response, and with too little depth the combing sits still and reads as coloration
      rather than motion.
    - Too fast a rate turns ensemble into warble. The effect should drift, not shake.
    - Summing chorus to mono keeps the combing but loses the width that stereo versions
      spread between channels ([Measuring sound](conventions.md) notes the mono scope).

## Related effects

- [Vibrato](vibrato.md): the wet path of this effect, heard alone.
- Flanger: the same structure with a shorter delay and more feedback.
- [Reverb](reverb.md): many fixed delays instead of one moving delay.

## Learn more

- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley — modulated delay
  effects, including chorus and flanging.
