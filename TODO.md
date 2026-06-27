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
- [ ] Chapter 2 — Limiting page (refs: `thirdparty/compare/` audacity look-ahead, sox)
- [ ] Chapter 2 — Expanding page (refs: dafx `compexp.m`, sox `compand`)
- [ ] Conventions: confirm depth/altitude after feedback

## Visualization
- [ ] Decide the browser viz stack (plain Canvas vs a charting lib) — DESIGN §4
- [ ] Adopt "two visuals per effect" (static curve + time-domain) per the AGC finding
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
