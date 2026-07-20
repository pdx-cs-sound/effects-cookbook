# Vibrato

> Vibrato varies a signal's pitch periodically. An LFO sweeps the length of a short delay
> line, and the sweep shifts the pitch.

*Chapter 7 — delay and modulation. The [LFO of Chapter 4](waveforms.md) pointed at a
delay time instead of a volume knob.*

---

!!! note "Vibrato is not tremolo"
    Vibrato modulates pitch; tremolo modulates volume ([Chapter 5](tremolo.md)). Decades
    of guitar amplifiers label a tremolo circuit "vibrato," so the label on an amplifier
    is unreliable. This page is the pitch effect.

## Intuition

A delay line holds a piece of the signal, and the read position slides along it like a
tape head. While the delay grows, the head moves against the signal and every cycle takes
longer to come out, so the pitch drops. While the delay shrinks, the pitch rises. A fixed
delay changes nothing about pitch. Only a changing delay does, and vibrato keeps the
delay changing by sweeping it with an LFO.

The size of the shift follows the rate of change. If the delay grows by $\Delta$ samples
per sample, the output pitch is scaled by $1 - \Delta$. The sweep is gentle, so the shift
stays within a few cents and reads as wobble rather than as a new note.

## Key parameters

| Parameter | What it controls |
|---|---|
| Rate | The LFO frequency (Hz). Musical vibrato sits near 5 Hz. |
| Depth | How far the delay swings (ms), and so how far the pitch swings. |
| Base delay | The center of the swing (ms). It adds a small fixed latency. |

## How it works

1. Run an LFO at the rate, mapped into $[0, 1]$.
2. Compute the moment's delay, base plus depth times the LFO value.
3. Read the delay line at that delay and emit the result. The output is the delayed
   signal only, with no dry mix.

The delay is fractional. An integer delay would jump one whole sample at a time, and each
jump would click. The read instead interpolates linearly between the two nearest stored
samples, for a fractional delay $D = i + f$:

$$
x[n-D] \approx (1-f) \cdot x[n-i] + f \cdot x[n-i-1]
$$

```python
--8<-- "code/delays.py:vibrato"
```

!!! warning "Pitfalls"
    - Too much depth or rate stops sounding like vibrato. Wide fast sweeps read as a
      siren or as seasickness. Musical settings stay small.
    - Linear interpolation dulls the highest frequencies slightly. Production pitch
      shifters use better interpolation; the trade is complexity.
    - The base delay is latency. A vibrato with a 5 ms base arrives 5 ms late, which is
      harmless in a recording and noticeable in a live monitor path.

## Related effects

- [Tremolo](tremolo.md): the same LFO pointed at volume. The pair are the two simplest
  modulation effects, and amplifiers confuse their names.
- [Chorus](chorus.md): this effect mixed with the original signal.

## Learn more

- Udo Zölzer (ed.), *DAFX: Digital Audio Effects*, 2nd ed., Wiley — delay-line
  modulation and interpolation.
