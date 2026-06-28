# Designing a compressor as a decision map (POSA-inspired)

> Working research note (not published content). 2026-06-27. An experiment in framing effect
> design the way Douglas Schmidt frames building a web server in **POSA** — as a graph of
> decisions and their ramifications, rather than one "correct" recipe.

## The idea & its provenance

In *Pattern-Oriented Software Architecture, Vol. 2: Patterns for Concurrent and Networked
Objects* (Schmidt, Stal, Rohnert & Buschmann, Wiley, 2000), Schmidt draws his **JAWS** web
server as a **pattern-relationship graph**: nodes are patterns, arrows are "uses / refines /
leads to," and the highlighted core is the event-handling/concurrency fork (Reactor, Proactor,
Leader/Followers, Half-Sync/Half-Async).

We borrow the **method**, not the patterns: present a compressor as *"here are the decisions you
must make — partially ordered, not a strict sequence — and what each choice costs and buys."*

> **Scope caveat (for §7 attribution):** POSA2's actual patterns are concurrency/threading/
> networking — exactly the material this cookbook excludes from its code (no threading). So we
> credit Schmidt's *decision-map approach*, not his patterns. Say so explicitly on the page.

## The decisions (nodes), each with its fork and ramification

1. **Detector domain** — *peak vs RMS* (vs loudness). Peak catches transients and protects
   against clipping; RMS is smoother and closer to perceived loudness. *(Core fork.)*
2. **Detector topology** — *feed-forward vs feedback*. Feed-forward (measure the input) is
   predictable and easy to analyze; feedback (measure the output) self-regulates and trends
   toward AGC-like behavior, but is harder to reason about. *(Core fork.)*
3. **Static transfer function** — *threshold + ratio*. The hub: how much gain reduction for a
   given level above threshold. Everything downstream refines or schedules this. *(Core fork.)*
4. **Knee** — *hard vs soft* (and the knee math: linear-ratio blend / quadratic gain spline /
   Bézier). Governs derivative continuity at the threshold — audible smoothness vs. an abrupt
   grab.
5. **Smoothing placement** — *before vs after the transfer function*. Smooth the detected
   *level*, or the computed *gain*? Both are valid and sound subtly different on transients.
6. **Ballistics** — *attack / release* time constants; fixed vs program-dependent. The source
   of pumping/breathing if mismatched to the material.
7. **Lookahead** — *none / plain delay / true pre-ramp*. Plain delay time-aligns an
   already-computed gain; true lookahead pre-ramps the reduction so it's fully in place when the
   transient arrives (zero overshoot) — at the cost of latency.
8. **Makeup gain** — *manual vs auto*. Restores loudness lost to gain reduction.

(Deferred as "advanced" for the simple compressor: channel linking, sidechain filtering,
oversampling/true-peak.)

## From "no design" to "a complete design" — the path is your choices

The structure is a **single-source, single-sink decision flow**, not a branching tree (a tree
would have many leaf endpoints; here every design converges on "complete"):

- **One START** = no design yet.
- You pass through **every** decision and pick **one option** at each (you don't branch *past*
  any decision — the branching is in the options, which then reconverge).
- **One END** = a complete compressor.
- A **path** through the flow = the series of choices = one specific design.

```
START (no design)
  │  detector domain   : peak | RMS
  │  topology          : feed-forward | feedback
  │  knee              : hard | soft
  │  smoothing         : before | after the transfer fn
  │  lookahead         : none | delay | true pre-ramp
  │  makeup gain       : manual | auto
  ▼
END (complete compressor)
```

**Ordering is a presentation choice, not a hard sequence.** A few real dependencies exist
(knee math presupposes a threshold/ratio transfer function; ballistics *is* the smoothing's
time behavior; lookahead only matters once attack latency exists), but several adjacent
decisions commute — so the row order is for legibility, and the "maybe not in this order" idea
survives as "you may revisit earlier choices."

## The payoff: the five reference implementations as paths

Each project in `thirdparty/compare/` (see its `analysis.md`) is a *different path* through the
same graph. Plotting them shows that "a compressor" is a **region in decision-space**, not one
algorithm:

| Decision | dafx | pcs | guitarix | sox | audacity |
|---|---|---|---|---|---|
| Detector domain | RMS | RMS / peak-to-peak | one-pole \|x\| (RMS opt.) | rectified peak | rectified peak |
| Topology | feed-fwd | feed-fwd | feed-fwd | feed-fwd | feed-fwd |
| Smoothing placement | after (gain) | none | before (level) | before (level) | after (gain) |
| Knee | hard (min of lines) | n/a | linear-ratio blend | Bézier piecewise | quadratic gain spline |
| Ballistics | attack/release | none | attack/release | attack/release | attack/release |
| Lookahead | faux delay | none | none | plain delay | true pre-ramp |
| Makeup | manual | upward "norm." | manual | manual | manual |

*(Data adapted from `thirdparty/compare/analysis.md`; verify against the sources before
publishing.)* Limiter, AGC, and expander become **other paths through the same map** — the
generalization step after the compressor prototype locks the format.

## Granularity check (does the map separate all five?)

Resolution is itself a design choice: too coarse and distinct designs collapse. The first cut
(binary knee) made guitarix and sox differ on only one chip and hid three different soft-knee
schemes. Refined options that separate all five on multiple axes:

- **Knee:** `hard | soft-linear | soft-quad | soft-curve` (separates guitarix / audacity / sox).
- **Smoothing:** add `none` → `none | before | after` (separates pcs).
- **Ballistics** (re-added): `none | fixed | program-dependent` (pcs has none).
- **Topology** kept for conceptual completeness, though all five are feed-forward (it does not
  separate *this* set — but feedback is real, e.g. AGC).

With these, every pair differs on ≥2 axes (dafx↔pcs on 4; guitarix↔sox on 2: knee + lookahead).
**Teaching point:** the right resolution is the one that separates the things that actually
sound different.

## Diagram

`visualization/compressor_decision_map.html` — **interactive**: single start ("no design") →
one option per row → single end ("complete compressor"), with the five `compare/`
implementations toggleable as distinct colored paths (parallel-nudged where they share a
choice). Next: hover-for-ramification per option; then generalize the flow to limiter / AGC /
expander.

## Open questions

- Does this live in the Compression page itself, or as a chapter-level "how to design one of
  these" interlude?
- Static diagram vs. interactive decision-walker?
- How explicit to make the POSA borrowing for a CS416/516 reader (footnote vs. sidebar).
