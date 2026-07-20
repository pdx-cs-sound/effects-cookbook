# TODO

Working task list for the Digital Audio Effects Cookbook. Design rationale lives in
[DESIGN.md](DESIGN.md); this is the actionable view.

## Now — ordered plan (updated 2026-07-13, post-feedback)
- [x] Feedback structure batch (2026-07-13): eleven chapters (5 = envelopes & tremolo,
      6 = Companding restored); mu-law dropped (archived `research/dropped-mu-law.md`);
      compressor design page folded into Compression; MathJax (arithmatex, $..$) enabled;
      top+bottom page nav enabled. Full list: `research/feedback-2026-07-13.md`
- [x] Feedback general batch done (2026-07-13): equations as math across ch. 2-6;
      algorithms-textbook pseudocode on the four companding pages (convention in DESIGN
      §3); ch. 2 notes (samples/sec, "Why mono only?", peak-to-peak subsection)
- [x] Feedback specifics batch done (2026-07-13): bit-crush arbitrary levels; asymmetric
      clipping (+ figure curve); sawtooth rising/falling; AGC reworked to fast attack /
      slow release (Woodgate-backed; Ed still owns extra reference validation)
- [x] Tone batch done (2026-07-13): STYLE.md rules 10 (plain punctuation) and 11 (no
      idioms); full-book sweep of dashes/semicolons/kickers/reversals/idioms; two stale
      Chapter-7 links caught by the audit and fixed
- [x] Detector run (2026-07-19): lexical tells scrubbed; residual flags are structural
      consistency, accepted as intentional (template + STYLE.md). Tone work closed.

### Superseded plan (2026-07-08)
- [x] Ten-chapter skeleton in place (stubs for ch. 3, 6–10 + tremolo; envelopes moved to
      ch. 4; AGC into ch. 5, tremolo-then-CLEA order; index/status/cross-links updated)
- [x] **Flat rewrite pass** done (2026-07-07): index, conventions (now titled "Measuring
      sound"), waveforms' moved section, compression, limiter, expander, agc. Load-bearing
      analogies kept per rule 5 (both fader analogies survive). Zero contractions / reader
      address / authorial "we" in prose; code comments exempt.
- [x] Chapter 3 drafted (2026-07-13): one page, four effects in causal order (volume →
      distortion → bit crush → mu-law), four linear transfer-curve figures added to
      `make_figures.py`, mu-law round-trip verified, appendix demos linked from the
      distortion section
- [x] Chapter 4 drafted (2026-07-13): sine → standard waveforms (figure + the book's first
      audio demos, 4 tones from `code/make_demos.py`) → phase-accumulator pattern (figure +
      float-wrap pitfall found by the test suite) → LFOs → envelopes (ADSR acknowledged,
      follower retained). Page code snippet-included from `code/oscillators.py` (tested;
      also feeds figures and demos).
- [x] Tremolo drafted (2026-07-13): Chapter 5 complete. `tremolo()` in oscillators.py
      (snippet-included, tested), figure, and the book's first before/after effect demo
      (plain tone vs. tremolo). Tremolo-vs-vibrato naming trap in pitfalls.
- [x] Chapter 7 drafted (2026-07-19): delay & modulation. `code/delays.py` (RingBuffer,
      echo, vibrato, chorus, comb/allpass, Schroeder reverb) with `code/test_delays.py`;
      four pages (delay-modulation, vibrato, chorus, reverb). Figures and audio demos
      deferred until Ed's read-through.
- [ ] Chapter 7 figures and audio demos (after Ed's read-through)
- [ ] First per-effect before/after audio demos (compressor on the burst tone?) using the
      make_demos pipeline

### Earlier plan (2026-07-05)
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
  - [ ] If/when a psychoacoustics section exists: an interactive loudness-matching tool
        (Ed's idea, 2026-07-13) — volume sliders on the ch. 4 waveform tones, adjusted by
        ear until they sound equally loud, then reveal the chosen offsets in dB. The reader
        generates their own equal-loudness data (the method behind ISO 226); ties to
        level-vs-loudness (ch. 2) and the subjective-testing discussion in
        `research/audio-quality-metrics.md`. Interactive-sound tier, appendix-first.
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
- [x] References appendix (`prototype/references.md`): five compressor sources with context,
      standards, texts; chapter one-liners link into it
- [x] Pending References links resolved and fetch-verified (2026-07-08): DAFX chapter-4 +
      MATLAB pages on dafx.de (compexp.m is inside `M_files_chap04.zip`); pcs =
      github.com/pdx-cs-sound/effects `compressor.py`
- [ ] Verify Woodgate / ISCVE Note 27.1 + IEC 60268-8 citation details
- [ ] Check WebRTC AGC2 license before quoting any code
- [ ] Replace placeholder references in `compression.md` with real, cited sources
- [ ] Redraw any borrowed figures (e.g. Woodgate Fig. 1) as our own before publishing

## Handoff (end of term)
- [ ] Document the expected build-and-validate process, local and CI, as a handoff
      deliverable. Much of it exists piecemeal — README (venv recreation, serve/build/test/
      check commands, .python-version), the publish workflow (tests + build + embed check
      gate deploy), `code/make_figures.py` for regenerating figures, the snippets include
      that ties `compressor.py` to the design page. The handoff doc should tie these
      together for whoever inherits the repo: what runs where, what failure looks like,
      and what to do about it.

## Housekeeping
- [x] `code/check_embeds.py` (2026-07-08, written by a Sonnet subagent, reviewed here):
      fails the build on dangling raw-HTML embeds (iframe/img/a/script/audio/source), which
      MkDocs link validation cannot see. Wired into the publish workflow before deploy,
      along with the unit tests.
- [ ] CI auto-deploy via GitHub Action (currently `gh-pages` via `mkdocs gh-deploy`) — DESIGN §4
- [ ] Confirm `requirements.txt` is pinned
