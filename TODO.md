# TODO

Working task list for the Digital Audio Effects Cookbook. Design rationale lives in
[DESIGN.md](DESIGN.md); this is the actionable view.

## Now — ordered plan (2026-07-02)
- [x] Skeleton pass: reader-facing scope/deferral notes consolidated into a published
      **Status & scope** appendix (`prototype/status.md`); author metadata stays in
      DESIGN/research; **Visualizations moved under Appendix**; Hear-it / Visualization
      placeholders and verify-citations footers removed from all chapters
- [x] Voice samples drafted: STYLE.md updated (lcamtuf touchstone, rule 9 "typography never
      carries information"); Limiting rewritten 3 ways in `research/voices/` (warm/Asimov,
      textbook/Prince, essay/lcamtuf) with a README of review questions
- [ ] Send STYLE.md + `research/voices/` to Massey; hold the full rewrite until he reacts
- [ ] While waiting on voice feedback: embed visualizations into chapters as needed
  - [x] Static-figure pipeline: `code/make_figures.py` (stdlib SVG, data from the book's own
        `compressor.py`) → `prototype/img/`; 7 figures embedded: Compression (transfer +
        gain-reduction), Limiting (transfer + lookahead-vs-overshoot), Expanding (transfer +
        gate trace), Conventions (envelope follower)
  - [ ] Embed the fixed AGC static-vs-time figure into the AGC page (iframe or rebuild as SVG)
  - [ ] Eyeball all 7 figures in both themes (dark-mode check) and at mobile width
- [ ] Audio-demo discussion note for the meeting (formats, hosting; proposal: self-generate
      demos with `code/compressor.py` + stdlib `wave` — zero deps, zero licensing questions)

## Content
- [x] Configurable reference compressor exercising every decision-map choice
      (`code/compressor.py`, 5 reference presets) + stdlib unittest suite
      (`code/test_compressor.py`, 23 tests) — run `python3 -m unittest discover -s code`
- [ ] Cookbook page walking the configurable reference compressor ("the decision map as code")
- [ ] Consider running the code tests in the publish GitHub Action (one extra step before deploy)
- [x] "Further complexity" knee questions (parabolic knee? smoothing before/after?) answered
      by the decision-map work — see `research/compressor-design-decisions.md` (knee schemes,
      smoothing placement); section since removed from the page
- [ ] Chapter 2 — Compression: refine existing prototype page
- [x] Chapter 2 — Limiting page drafted (`prototype/limiter.md`)
- [x] Chapter 2 — Expanding page drafted (`prototype/expander.md`)
- [ ] Add "Hear it" / Visualization content to limiter + expander once stack is settled
- [ ] Conventions: confirm depth/altitude after feedback
- [x] Units-rigor pass on Conventions (dB always names a reference; power=10·log/amplitude=20·log;
      dBFS peak-primary + always label peak/RMS; decline AES17 offset; level vs loudness vs volume)
      — addresses the "be rigorous about units" feedback
- [ ] Later / TBD: loudness units (phon, sone), LUFS (BS.1770), psychoacoustics, A-weighting/dBA
- [x] Gather citable audio-evaluation-metric sources (`research/audio-quality-metrics.md`)
- [ ] Consider a per-effect "How do we measure it?" section — crest factor + LUFS (BS.1770/R128)
      for the dynamics effects; reproducible counterpoint to subjective listening tests

## Visualization
- [ ] Decide the browser viz stack (plain Canvas vs a charting lib) — DESIGN §4
- [ ] Adopt "two visuals per effect" (static curve + time-domain) per the AGC finding
- [x] POSA-style compressor "design decision map" — single start/end flow, refined granularity,
      interactive five-implementation overlay (`prototype/visualization/compressor_decision_map.html`,
      note in `research/compressor-design-decisions.md`)
- [ ] Next on the decision map: hover-for-ramification per option; then generalize the flow to
      limiter / AGC / expander (other paths through the same decisions)
- [x] Visualizations gallery page (`prototype/visualizations.md`); moved `visualization/` into
      `docs_dir` (now `prototype/visualization/`) so the figures are served and embeddable
- [ ] Embed individual visuals directly into their effect pages (beyond the gallery)
- [ ] Build the "Planned" gallery figures (static transfer curve, crest factor/LUFS, envelope follower)

## Open design decisions (DESIGN §4)
- [ ] Prose style: `STYLE.md` drafted (plain expository register, 8 rules, tics-to-cut list,
      sample rewrite, open questions) — waiting for feedback
- [ ] Conventions chapter scope: how much foundational material in Ch1 vs per effect
- [ ] Pseudocode conventions (format, closeness to Python)
- [ ] Authoring workflow (branch / PR / review)
- [ ] Per-effect companion notebook? (y/n)
- [ ] Project license — content vs code (§7)

## Attribution & verification (§7)
- [ ] Verify Woodgate / ISCVE Note 27.1 + IEC 60268-8 citation details
- [ ] Check WebRTC AGC2 license before quoting any code
- [ ] Replace placeholder references in `compression.md` with real, cited sources
- [ ] Redraw any borrowed figures (e.g. Woodgate Fig. 1) as our own before publishing

## Housekeeping
- [ ] CI auto-deploy via GitHub Action (currently `gh-pages` via `mkdocs gh-deploy`) — DESIGN §4
- [ ] Confirm `requirements.txt` is pinned
