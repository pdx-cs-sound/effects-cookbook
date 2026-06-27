# Digital Audio Effects Cookbook — Design Doc

> Status: **DRAFT** — living document. `TBD` marks open decisions.
> Course context: produced under **PSU CS506** (a special-projects course, with Massey). The
> intended *audience* is **CS416/516** students (the class likely to be pointed at this work).
> First content: **two chapters** — (1) *Conventions & AGC* and (2) *Companding* (compression, limiting, expanding).

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
- **Scope of v1:** **two chapters** —
  - **Chapter 1 — Conventions & AGC:** shared vocabulary (samples & the [-1,1] range, dB and
    **dBFS**, peak vs RMS level detection, linear↔dB gain, attack/release time constants),
    then Automatic Gain Control.
  - **Chapter 2 — Companding:** compression, limiting, and expanding (the threshold-and-ratio family).
- **Future effects (backlog):** TBD (EQ, reverb, delay, distortion, etc.)

### Explicit non-goals (scoping)
- **No analog effects or analog explanations** — digital-domain only (the math, plus scoping).
- **Not production code.** No "drop this into a GarageBand plugin," no test harness, no `numpy`,
  no threading. Reference code is illustrative, self-contained, pure standard library.
- **No AI coverage** — neither AI-based effects nor AI-assisted *use* of these effects.
  (Using AI for *our own* research/planning is fine.)
- **Measurement unit: dBFS** (decibels relative to full scale). *Replaces the earlier dBA
  decision (2026-06-27).* dBFS is the natural unit for sample-domain work in `[-1, 1]` and is
  what the reference code already computes. dBA / A-weighting may be *mentioned* in the
  Conventions chapter as related context, but is **not** the working unit.

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
> - **Structure = two chapters** (2026-06-27): Ch1 *Conventions & AGC*, Ch2 *Companding*
>   (compression, limiting, expanding). Supersedes the earlier one-chapter-per-concept plan.
>   Each effect within a chapter still uses the template below.
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
- **Measurement unit:** dBFS (updated 2026-06-27, was dBA).
- **Structure:** two chapters — Conventions & AGC; Companding (updated 2026-06-27).
- **Language, split by role:**
  - **Example / teaching code = basic Python** (standard library, no deps) — this is what we
    hand students.
  - **Visualization & display = runs in the browser** (JavaScript / Web Audio / Canvas — exact
    stack TBD). Whatever powers the visuals must run client-side in the rendered docs.

**Still TBD:**
- **Conventions chapter scope:** how much foundational material (samples, dB/dBFS math, peak
  vs RMS, gain, time constants) lives in Chapter 1 vs. is restated per effect.
  *(The earlier dBA-only / A-weighting question is closed — dBFS is the unit. See Decision Log.)*
- **Visualization stack:** which browser tech produces the visuals (plain Canvas? a charting
  lib? Web Audio-driven?). Display language is settled (browser); the specific stack isn't.
- **Pseudocode style/conventions** (format, how close to the chosen language).
- **Authoring workflow** (who writes, how reviewed, branch/PR process).
- **Per-effect companion notebook?** (yes/no — pairs with MkDocs page).
- **Repo name / GitHub Pages URL.**

## 5. Content Notes — the two chapters

**Chapter 1 — Conventions & AGC**
- *Conventions:* samples & the `[-1,1]` range, dB and **dBFS**, peak vs RMS level detection,
  linear↔dB gain, attack/release time constants. The shared vocabulary the rest of the book
  leans on. (Optionally mention dBA / A-weighting as related context — not the working unit.)
- *AGC:* automatically holds level near a target over time (slow, feedback). Best taught as a
  **goal** ("hold a target level automatically") realized as a **control technique** — not a
  single canonical algorithm. See the taxonomy below.

**Chapter 2 — Companding** (compression, limiting, expanding)
- *Compression:* reduces dynamic range above a threshold (ratio, attack, release, knee, makeup).
  Existing prototype: [prototype/compression.md](prototype/compression.md).
- *Limiting:* compression at ∞:1 (or very high) ratio with fast attack.
- *Expanding:* the inverse — turns *down* quiet parts (gate = extreme expander).
- Resources: the `thirdparty/compare/` folder + its `analysis.md` cover compression,
  expansion (dafx `compexp.m`, sox `compand`), and true look-ahead limiting (audacity).

### AGC / limiting / compression taxonomy (research, 2026-06-27)

Primary source: **J. M. Woodgate, ISCVE Engineering Note 27.1**, "Automatic gain control,
limiting and compression" (anchored to **IEC 60268-8**). Woodgate notes the distinction
"seems not to be clearly documented anywhere" — which is why AGC felt under-specified. He
characterizes all three by two axes — **control-loop gain** (how flat the output is held) ×
**release time-constant** (slow vs fast):

| | Output held ~constant (high loop gain) | Output less-than-proportional (moderate gain) |
|---|---|---|
| **Slow release (≥ 1 s)** | **AGC** — *transparent* (no subjective-quality change) | — |
| **Fast release (~ms)** | **Limiting** — *audible* | **Compression** — *audible* |

Teaching consequences:
- **Limiting is the bridge** between the chapters: AGC's flattening + compression's speed.
- **Transparency criterion:** AGC (done right) doesn't change subjective quality; compression
  & limiting deliberately do → "corrective/transparent" vs "creative/audible."
- **Unifying view:** all are the same static transfer curve at different **ratios** —
  compression (e.g. 2, 3) vs limiter/AGC (∞). See Figure-1 note below.
- **Topology caveat:** Woodgate's axes are behavioral/topology-agnostic. Implementation-wise,
  AGC is typically **feedback** (senses output); the `compare/` compressors are **feed-forward**
  (sense input). Teach behavior as primary, topology as a secondary note.
- **Scope caveat:** the note is installed-sound/analog-era (e.m.f, AFILS hearing loops) — cite
  it for the *taxonomy* only (topology-independent, applies to dBFS digital), not circuit detail.

**Figure 1 (static output/input curve) insight:** a steady-state transfer plot **cannot
distinguish AGC from a limiter** — Woodgate literally labels them one line ("AGC or limiter").
What separates them (release time) lives in the **time domain**, invisible on a static curve.
→ Strong argument that each effect page needs **two** visuals: a static transfer curve *and* a
time-domain/envelope view. The static axis = "how flat" (ratio); the missing axis = "how fast"
(release). Below threshold all curves are unity (1:1, untouched).

Citable sources gathered: Woodgate / ISCVE Note 27.1 + IEC 60268-8; Zölzer (ed.) *DAFX*;
WebRTC **AGC2** (modern digital, browser-relevant — check license before quoting code);
Wikipedia *Automatic gain control* (definition only — heavily analog/radio).

**Status / action items:**
- Reference code already uses **dBFS** (raw `20·log10` detector) — aligns with the new unit. ✔
- `compress()` is numpy-free, `math`-only. ✔
- AGC research pass — **done** (taxonomy + sources above). Limiting/expanding references exist
  in `thirdparty/compare/`. ✔
- Open: verify the Woodgate/IEC + WebRTC license details before publishing (per §7).
- Add the **Visualization** section per page once a browser stack is settled — likely
  **two** views per effect (static curve + time-domain). Two viz prototypes exist under
  `visualization/`.

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
| 2026-06-27 | **Restructured to two chapters:** Ch1 Conventions & AGC, Ch2 Companding (compression, limiting, expanding) — supersedes one-chapter-per-concept | Group the threshold-and-ratio family; put shared conventions up front |
| 2026-06-27 | **Measurement unit dBA → dBFS** | dBFS is the natural sample-domain unit and what the code already computes; A-weighting out of scope as the working unit |
| 2026-06-27 | Adopt Woodgate/IEC 60268-8 **loop-gain × release-time taxonomy** for AGC/limiting/compression; teach AGC as goal+technique | Authoritative, topology-agnostic; maps cleanly onto the two chapters (limiting bridges them) |
| 2026-06-27 | Plan **two visuals per effect** (static transfer curve + time-domain) | A static curve can't distinguish AGC from a limiter; the difference is in the time domain |
