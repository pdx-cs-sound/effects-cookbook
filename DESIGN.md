# Digital Audio Effects Cookbook — Design Doc

> Status: **DRAFT** — living document. `TBD` marks open decisions.
> Course context: produced under **PSU CS506** (a special-projects course, with Massey). The
> intended *audience* is **CS416/516** students (the class likely to be pointed at this work).
> First content: the **volume/level effects pair** — Compression & Automatic Gain Control (AGC).

---

## 1. Purpose

An educational "cookbook" for digital audio effects. Each effect is explained at multiple
levels of abstraction so a reader can learn it the way that suits them:

1. **Plain-language text** — what the effect does, why, when to use it.
2. **Pseudocode** — the algorithm, language-agnostic.
3. **Real code** — a working implementation.
4. **Links** — references to go deeper.

Cookbook ethos: consistent template per effect, copy-pasteable, learn-by-doing.

## 2. Audience & Scope

- **Audience:** a CS416/516 student or self-educator who wants to go deeper. This cookbook is
  a *"learn more here"* gateway — each page should teach the effect **and** link onward so the
  reader can keep going from our references.
- **Depth target:** level **1–2** on a 1–3 scale where 1 = competent practitioner,
  2 = everyday worker in the space, 3 = dissertation-grade. We aim at **1, occasionally 2**.
  Explicitly **not** state-of-the-art; we are not pushing the envelope.
- **Prerequisites assumed:** TBD (basic programming; comfort with samples and dB).
- **Scope of v1:** Compression and AGC — **one chapter per concept** (cross-linked, not merged).
- **Future effects (backlog):** TBD (EQ, reverb, delay, distortion, etc.)

### Explicit non-goals (scoping)
- **No analog effects or analog explanations** — digital-domain only (the math, plus scoping).
- **Not production code.** No "drop this into a GarageBand plugin," no test harness, no `numpy`,
  no threading. Reference code is illustrative, self-contained, pure standard library.
- **No AI coverage** — neither AI-based effects nor AI-assisted *use* of these effects.
  (Using AI for *our own* research/planning is fine.)
- **Measurement unit: dBA only** ([A-weighting](https://en.wikipedia.org/wiki/A-weighting)).
  dBA will be introduced as a **foundational concept** somewhere (placement TBD). *Interim
  approach (a):* treat dBA as the reporting convention; detector stays simple. How deep we go
  (whether we ever implement A-weighting) is an **open question** — see §4.

## 3. Per-Effect Page Template (the core artifact)

Proposed sections for every effect entry:

| Section | Purpose |
|---|---|
| Title + one-line definition | Orient the reader fast |
| Intuition / what & why | Plain language, maybe an analogy |
| Audible example | Before/after audio — TBD whether interactive |
| Key parameters | e.g. threshold, ratio, attack, release |
| How it works | Conceptual walk-through, diagrams |
| Visualization | Some visual of the effect in action — medium TBD (see §4). |
| Pseudocode | Language-agnostic algorithm |
| Reference implementation | Real, runnable code |
| Pitfalls / gotchas | Common mistakes |
| Related effects | Cross-links (e.g. Compression ↔ AGC ↔ Limiter) |
| Learn more | External links / papers / books |

> Decisions:
> - **Granularity = one chapter per concept.** Compression and AGC are *separate* chapters,
>   cross-linked — not a single merged "pair" page.
> - Lock this template using Compression as the prototype, then reuse.

## 4. Decisions & Open Criteria

**Settled (2026-06-25):**
- **Interactivity:** Start static (text + code). Design the template so audio demos
  (pre-rendered clips first, live Web Audio later) slot in without rework.
- **Delivery / stack:** MkDocs Material → GitHub Pages (Markdown content, auto-deploy
  via GitHub Action). Runner-up considered: Jupyter notebooks (kept as optional
  "run it yourself" companion per effect).
- **Audience & depth:** CS416/516 student or self-educator; depth level 1–2; not SOTA (§2).
- **Non-goals locked:** no analog, no AI effects/usage, not production, no `numpy`/threading/harness (§2).
- **Measurement unit:** dBA only.
- **Granularity:** one chapter per concept (§3).
- **Language, split by role:**
  - **Example / teaching code = basic Python** (standard library, no deps) — this is what we
    hand students.
  - **Visualization & display = runs in the browser** (JavaScript / Web Audio / Canvas — exact
    stack TBD). Whatever powers the visuals must run client-side in the rendered docs.

**Still TBD:**
- **`dBA` scope (open question):** *interim = (a)* dBA is the reporting convention only;
  detector stays simple. The deeper option — actually implementing/explaining an A-weighting
  filter in the detector — is **unresolved**. Also TBD: **where** dBA gets introduced as a
  foundational concept (its own page vs. inside Compression).
- **Visualization stack:** which browser tech produces the visuals (plain Canvas? a charting
  lib? Web Audio-driven?). Display language is settled (browser); the specific stack isn't.
- **Pseudocode style/conventions** (format, how close to the chosen language).
- **Authoring workflow** (who writes, how reviewed, branch/PR process).
- **Per-effect companion notebook?** (yes/no — pairs with MkDocs page).
- **Repo name / GitHub Pages URL.**

## 5. Compression & AGC — Content Notes

- Compression: reduces dynamic range above a threshold (ratio, attack, release, knee, makeup gain).
- AGC: automatically targets a level over time (slower, feedback-driven).
- **Teaching angle:** both control level, but differ in intent, time constants, and feedback —
  good compare/contrast. **One chapter each**, cross-linked (no merged page).
- Existing asset: compression code from prior session (TBD — locate & link in).

**Action items from the new guidelines (apply to [prototype/compression.md](prototype/compression.md)):**
- ~~Rewrite the reference `compress()` to pure standard-library Python~~ **DONE (2026-06-25)** —
  numpy removed; now `math`-only, operates on plain lists.
- **Express level detection in dBA** once the dBA-scope question is settled (the current draft
  still uses a raw `20·log10` peak detector — deferred per decision).
- Add the **Visualization** section once a browser stack is chosen.

## 6. Prototypes / Samples

Goal: mock the Compression page enough to guide decisions before committing to a stack.
- Status: TBD (see conversation)

## 7. Attribution & Licensing

The project is **rigorous about attribution and copyright.** Working policy (refine as needed):

- **Cite every source.** Any text, equation, algorithm, or code idea adapted from a book,
  paper, blog, or repo gets an explicit citation in that page's *Learn more* / inline notes.
- **Code provenance.** Reference implementations are either original or clearly attributed to
  their source with the source's license noted. No uncredited copy-paste (e.g. musicdsp.org
  snippets carry their attribution).
- **Audio assets.** Any demo audio must be self-recorded, public-domain, or appropriately
  licensed (e.g. CC) — with source + license recorded. No "borrowed" clips.
- **Images/diagrams.** Same bar: original, or licensed-and-attributed.
- **Project license: TBD** (content vs. code may differ — e.g. CC-BY for prose, MIT for code).

## 8. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-06-25 | Project kicked off; cookbook model + per-effect template adopted as starting frame | Consistent template makes each new effect low-effort |
| 2026-06-25 | Static-first, audio-ready template | Ship reading/reference now; avoid rework when audio added |
| 2026-06-25 | Stack = MkDocs Material on GitHub Pages | Python tool, Markdown content, free hosting, cookbook-friendly features |
| 2026-06-25 | Audience = CS416/516 student / self-educator; depth level 1–2; not SOTA | Sets scope and tone; gateway "learn more here" resource |
| 2026-06-25 | Non-goals locked: no analog, no AI effects/usage, not production, no numpy/threading/harness | Keeps math + scope tractable for the depth target |
| 2026-06-25 | Measurement unit = dBA only | Single, consistent level convention across effects |
| 2026-06-25 | One chapter per concept (Compression and AGC separate) | Cleaner navigation; each concept stands alone |
| 2026-06-25 | Language split by role: teaching code = basic Python; visualization/display = browser (JS) | Hand students simple Python; visuals must run client-side in the docs |
| 2026-06-25 | dBA scope: interim (a) reporting-convention only; full A-weighting unresolved | Avoid over-engineering the detector at depth 1–2; revisit later |
