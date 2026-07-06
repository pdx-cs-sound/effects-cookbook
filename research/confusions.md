# Confusions log

Raw data: questions as they were actually asked, written down before the answer overwrote
them. The premise is the curse of knowledge — once a thing clicks, the question that
preceded it is hard to reconstruct, and the questions are where readers will stumble too.
Some entries become worked examples, pitfalls, or figure conventions; some get thrown away.
Both outcomes are fine. Capture first, judge later.

Format: the question in its original phrasing (or close), then what it turned into, if
anything.

## Banked (2026-06 – 2026-07)

1. "What is the difference between bel and decibel?"
   → groundwork for the Conventions units section.
2. "Power ratios — but a ratio of what, exactly? One value is the thing measured, what's
   the other?"
   → "A decibel is a ratio — so it always needs a reference" (Conventions).
3. "So dB doesn't tell you if you're measuring power or amplitude?"
   → the 10-vs-20 subsection and the reference table's quantity column.
4. "There are essentially 3 different dBFS measurements — we can't just assume one."
   → the peak/RMS labeling policy; AES17 offset explicitly declined.
5. "Does 'make this twice as loud' or 'make this 6 dB louder' have a precise meaning?"
   → "Level vs. loudness vs. volume" (Conventions), the three-doublings table.
6. Reviewer: "max P-P amplitude is 2, max sine RMS is 1.414 — make sure consistent." Author
   agreed the RMS figure without blinking.
   → "Peak-to-peak is not a level" warning; the RMS ≤ peak ≤ 1.0 sanity check.
7. "RMS power of a peak-1 sine is √2/2, so 10·log10 gives −1.5. What am I missing?"
   → the worked example: two correct routes to −3.01, and the halved-dB fingerprint of a
   10/20 mix-up.
8. "Is AGC an effect, a technique created by arranging effects, or a high-level goal?"
   → the framing device of the AGC chapter.
9. "I've heard 'railroad tracks' for this kind of decision mapping but can't find any
   references."
   → the naming-and-lineages section (railroad diagrams, Zwicky, feature models) in
   `compressor-design-decisions.md`.
10. "The decision tree needs one start point and one end point."
    → the decision map restructured to single-source/single-sink; path = design.
11. "Are the choices granular enough that all 5 implementations will look different?"
    → the granularity check; resolution-is-a-design-choice teaching point.
12. "The time-domain graph has 4 legend items but they don't align correctly."
    → convention: legend swatches carry the same stroke and dash as their lines.
13. "Why is the limiter holding the top at −10 but the bottom at −35/−28?"
    → convention: an effect's inactive stretches (output = input) must not render like
    active behavior. Also surfaced the one-sided/two-sided AGC-vs-limiter contrast.
14. "Why is the limiter holding −10 when the target is −20?"
    → convention: every reference level an effect owns gets drawn and named (target vs.
    ceiling are different effects' parameters).
15. "'Keeping a single honest reference' reads weird — like emphasizing several ways at
    once."
    → STYLE.md rule 6 extension: verdict adjectives; argue or conclude, not both.

## Open

*(Add new ones here as one-liners, before resolving them.)*

16. "I'm unclear if the limiter graph is supposed to be showing how the limiter doesn't
    care about undershooting." (limiter_lookahead.svg — is the quiet-section behavior a
    message or an accident? Suggests the figure isn't declaring its subject, or the
    faint/bold grammar isn't self-evident yet.)
17. Legend placement quibbles on the generated figures (details TBD after feedback round).
