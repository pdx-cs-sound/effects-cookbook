# Prose Style Guide

> Status: **PROPOSAL** — drafted for Massey's review before any rewrite pass.
> Scope: the cookbook pages in `prototype/`. Code comments and docstrings follow the
> spirit but favor precision over style.

## The target register

Plain expository prose. The models are Asimov's non-fiction and Simon Prince's
*Understanding Deep Learning*: short declarative sentences, the concrete case before the
general rule, and no rhetorical performance. Orwell's summary is the shortest version:
"good prose is like a windowpane."

The current pages do not yet follow this guide. They were drafted quickly and some of the
prose reads machine-generated. A rewrite pass is planned once this guide is settled.

## Rules

Each rule is checkable during review.

1. **Prefer short declarative sentences in the active voice.** A sentence may state a fact
   and stop. It does not need a payoff.
2. **Concrete before abstract.** Give the example or the motivation first, then the general
   rule, then the term for it.
3. **Define a term at first use, then use it consistently.** Do not rotate synonyms for
   variety. If the word is "level," it stays "level" (see the Conventions page for the
   level / loudness / volume distinction).
4. **Bullets are for enumerable things** — parameters, options, steps. If the items are
   sentences building an argument, write a paragraph.
5. **One analogy per section, and it must teach.** An analogy that only decorates gets cut.
6. **State claims without selling them.** Cut "beautiful," "powerful," "elegant,"
   "crucially," "the key insight." If a fact matters, its placement shows that.
7. **Hedge only with information.** "About 3 dB" is a hedge that informs; "arguably" and
   "somewhat" are hedges that stall.
8. **Cite or qualify empirical claims.** A perceptual or historical claim gets a citation,
   a number, or an explicit "rule of thumb" label (per DESIGN.md §7).

## Tics to cut

These patterns are the main reason the current prose reads machine-generated:

- Em-dash chains ("X — Y — Z"). Ration em-dashes to one pair per paragraph.
- Reversal constructions ("it's not X, it's Y"; "X isn't just Y — it's Z").
- Kicker sentences that end every paragraph on a beat.
- Balanced triples used as rhythm rather than because the list has three members.
- Bold-led parallel bullet lists where a paragraph would carry the argument.
- Rhetorical questions as transitions. (A question the text genuinely poses and answers,
  like "is AGC an effect, a technique, or a goal?", is fine.)
- Dramatic colons introducing a reveal.

## Sample rewrite

From the Conventions page, current:

> But getting this rigorous means being careful about three things that everyday usage
> blurs: a dB always implies a *reference*, it depends on whether you're measuring *power
> or amplitude*, and "dBFS" itself is only fully specified once you say *peak or RMS*.

Rewritten to this guide:

> Three details matter here, and everyday usage blurs all of them. A dB is always relative
> to a reference. The formula differs for power and for amplitude. A dBFS figure means
> nothing until you say whether it is peak or RMS.

Same content, four short sentences, no italics doing the emphasis work.

## Open questions

1. **Warmth.** Asimov talks to the reader ("you," contractions, first person); Prince is
   textbook-neutral. Where on that dial should this cookbook sit? The current draft pages
   lean Asimov.
2. **"We."** Acceptable for authorial decisions ("we measure in dBFS"), or prefer
   impersonal constructions?
3. **House spelling and mechanics.** US spelling? Oxford comma? Contractions?
4. **Anything you'd add or veto** in the rules above.
