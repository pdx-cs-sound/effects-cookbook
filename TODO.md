# TODO

Working task list for the Digital Audio Effects Cookbook. Design rationale lives in
[DESIGN.md](DESIGN.md); this is the actionable view.

## Now
- [x] Chapter 1 — Conventions page drafted (`prototype/conventions.md`)
- [x] AGC research pass → Woodgate/IEC taxonomy (DESIGN §5)
- [x] Chapter 1 — AGC page drafted (`prototype/agc.md`)
- [x] Two-panel static-transfer + time-domain visualization mock (`visualization/agc_static_vs_time.html`)
- [ ] Monday meeting with Massey — gather high- and low-level feedback

## Content
- [ ] Chapter 2 — Compression: refine existing prototype; answer the "Further complexity"
      knee questions (parabolic knee, smoothing before/after the transfer fn)
- [x] Chapter 2 — Limiting page drafted (`prototype/limiter.md`)
- [x] Chapter 2 — Expanding page drafted (`prototype/expander.md`)
- [ ] Add "Hear it" / Visualization content to limiter + expander once stack is settled
- [ ] Conventions: confirm depth/altitude after feedback
- [x] Gather citable audio-evaluation-metric sources (`research/audio-quality-metrics.md`)
- [ ] Consider a per-effect "How do we measure it?" section — crest factor + LUFS (BS.1770/R128)
      for the dynamics effects; reproducible counterpoint to subjective listening tests

## Visualization
- [ ] Decide the browser viz stack (plain Canvas vs a charting lib) — DESIGN §4
- [ ] Adopt "two visuals per effect" (static curve + time-domain) per the AGC finding
- [x] POSA-style compressor "design decision map" — single start/end flow, refined granularity,
      interactive five-implementation overlay (`visualization/compressor_decision_map.html`,
      note in `research/compressor-design-decisions.md`)
- [ ] Next on the decision map: hover-for-ramification per option; then generalize the flow to
      limiter / AGC / expander (other paths through the same decisions)
- [ ] Embed visuals into the MkDocs pages (currently `visualization/` is outside `docs_dir`)

## Open design decisions (DESIGN §4)
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
