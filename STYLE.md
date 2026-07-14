# Prose Style Guide

> Status: **register decided (2026-07-06): flat** — see `research/voices/limiting-flat.md`
> for the reference sample. The rules below stand; the open questions at the end are
> narrowed accordingly. Scope: the cookbook pages in `prototype/`. Code comments and
> docstrings follow the spirit but favor precision over style.

## The target register

Plain expository prose. The models are Asimov's non-fiction, Simon Prince's
*Understanding Deep Learning*, and Michał Zalewski's lcamtuf essays
(e.g. [lcamtuf.substack.com](https://lcamtuf.substack.com/)): short declarative sentences,
the concrete case before the general rule, and no rhetorical performance. Orwell's summary
is the shortest version: "good prose is like a windowpane."

Voice samples for comparison live in `research/voices/` — the Limiting chapter rewritten
four ways, from warm to flat. Pick a voice (or a blend) there before any full rewrite pass.

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
   "crucially," "the key insight." If a fact matters, its placement shows that. The same
   goes for verdict adjectives on technical nouns — "an honest reference," "a clean
   separation," "sane defaults." An adjective must specify a property the reader could
   check ("single," "fixed," "one-pole"); if it delivers a judgment instead, delete it and
   let the stated consequence make the case. A sentence should argue or conclude, not both.
7. **Hedge only with information.** "About 3 dB" is a hedge that informs; "arguably" and
   "somewhat" are hedges that stall.
8. **Cite or qualify empirical claims.** A perceptual or historical claim gets a citation,
   a number, or an explicit "rule of thumb" label (per DESIGN.md §7).
9. **Typography never carries information.** Strip the bold and italics from a sentence and
   it must lose nothing. Emphasis comes from sentence structure and word order; a definition
   is marked by phrasing ("called the threshold"), not by styling.
10. **Complete sentences, plain punctuation** (2026-07-13). No sentence fragments. Colons,
    semicolons, and dashes are rare; prefer separate sentences. A colon may introduce a
    list, an equation, or a code block. Structural uses are exempt: page subtitles,
    chapter-list separators, table cells, and bibliography entries.
11. **No idioms or figures of speech** (2026-07-13). "In the wild," "earns its keep,"
    "chew on": say the literal thing. A load-bearing analogy (rule 5) is not an idiom; the
    difference is that an analogy is introduced, developed, and used to teach.

## Tics to cut

These patterns are the main reason the current prose reads machine-generated:

- Em-dashes almost anywhere in prose (rule 10). Parenthetical asides become parentheses
  or their own sentence.
- Reversal constructions ("it's not X, it's Y"; "X isn't just Y — it's Z").
- Kicker sentences that end every paragraph on a beat.
- Balanced triples used as rhythm rather than because the list has three members.
- Bold-led parallel bullet lists where a paragraph would carry the argument.
- Rhetorical questions as transitions. (A question the text genuinely poses and answers,
  like "is AGC an effect, a technique, or a goal?", is fine.)
- Dramatic colons introducing a reveal.
- Bold or italics doing work that word order should do (see rule 9).
- Verdict adjectives standing in for the reason: honest, clean, sane, proper, principled,
  natural, elegant — and their adverbs (genuinely, simply, actually).

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

Warmth and person are settled by the flat decision: no reader address, no authorial "we,"
no contractions, no humor. Analogies are settled too (2026-07-07): load-bearing analogies
stay, per rule 5 — flat applies to delivery, not to pedagogy.

Mechanics (settled 2026-07-07): **US spelling** (labeled, behavior, analyzed) and the
**Oxford comma**, everywhere including code comments and docstrings.

No open questions at present.
