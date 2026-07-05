# Digital Audio Effects Cookbook

> An educational, work-in-progress cookbook for **digital** audio effects. Each effect is
> explained at several levels — plain language, pseudocode, real (runnable) code, and links to
> go deeper — so you can learn it the way that suits you.

*Produced under PSU CS506 (with Massey); aimed at CS416/516 students and self-learners who want
to go past "turn this knob" and understand how these effects actually work.*

---

## Start here

New to this? Begin with the **[Conventions](conventions.md)** page — it sets up the shared
vocabulary (samples, dBFS, level detection, gain, attack/release) that every effect page builds
on. Then read the effects in either chapter.

## Chapter 1 — Conventions & AGC

- **[Conventions](conventions.md)** — how we represent audio, measure level in dBFS, and follow
  a signal over time. The foundation.
- **[Automatic Gain Control](agc.md)** — holding a level near a target, automatically and
  transparently.

## Chapter 2 — Companding

The threshold-and-ratio family — **com**pressing and ex**pand**ing:

- **[Compression](compression.md)** — taming the loud parts to even out dynamics.
- **[Limiting](limiter.md)** — a brick wall: the signal never crosses a ceiling.
- **[Expanding](expander.md)** — the inverse: pushing the quiet parts down (a gate at the extreme).

## How each effect page is laid out

Every effect follows the same template: a plain-language **intuition**, the **key parameters**,
a **how it works** walk-through, **pseudocode**, a **reference implementation** in Python, the
**pitfalls**, related effects, and citations to learn more.

!!! note "Scope"
    Reference code is dependency-free Python meant to teach, not to ship; levels are in dBFS;
    the book stays in the digital domain. The full list of scope decisions and deferred
    topics is in [Status & scope](status.md).
