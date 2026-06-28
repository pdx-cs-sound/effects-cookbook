# Audio quality & evaluation metrics — citable sources

> Working research note (not published content). Gathered 2026-06-27. Verify each citation —
> exact revision/year/venue — before it appears in a published page, per DESIGN.md §7.

Organised in three tiers, trading **reproducibility** against how well each predicts human
perception. The subjective "gold standard" we're trying to avoid (expensive, listener
post-screening) is a **MUSHRA** or **BS.1116** test.

## The subjective baseline (what objective metrics try to replace)

- **MUSHRA** — ITU-R Rec. **BS.1534** (MUlti-Stimulus test with Hidden Reference and Anchor).
  Standard post-screening excludes listeners who rate the hidden reference too low.
  <https://www.itu.int/rec/R-REC-BS.1534>
- **BS.1116** — ITU-R Rec. **BS.1116** (small-impairment double-blind triple-stimulus).
  <https://www.itu.int/rec/R-REC-BS.1116>

## Tier 1 — Signal-fidelity / error metrics (full-reference, fully reproducible)

- **THD / THD+N / IMD** — classic distortion measures; defined across AES/IEC test standards
  (no single canonical paper; cite a standards text or IEEE/AES reference).
- **SNR, segmental SNR, log-spectral distance, mel-cepstral distortion (MCD)** — long-standing
  speech/audio error measures.
- **SI-SDR** (scale-invariant signal-to-distortion ratio) — Le Roux, Wisdom, Erdogan, Hershey,
  "SDR – Half-Baked or Well Done?", ICASSP 2019. doi:10.1109/ICASSP.2019.8683855.
  <https://arxiv.org/abs/1811.02508>
- **ESR (error-to-signal ratio)** + **multi-resolution STFT loss** — the metrics used in neural
  modeling of audio *effects*. Collected in **auraloss**: Steinmetz & Reiss, "auraloss:
  Audio-focused loss functions in PyTorch", DMRN+15, 2020. ESR ← Wright & Välimäki (2019);
  MR-STFT ← Yamamoto et al. (2019). Library: <https://github.com/csteinmetz1/auraloss>
  *(Notable: auraloss's own demo trains a model to emulate a **dynamic-range compressor** —
  directly relevant to this cookbook.)*

## Tier 2 — Perceptual objective models (deterministic, calibrated to listening tests)

- **PEAQ** — ITU-R Rec. **BS.1387** (Perceptual Evaluation of Audio Quality; basic & advanced
  models; outputs Objective Difference Grade). Open impl: GstPEAQ.
  <https://www.itu.int/rec/R-REC-BS.1387>
- **ViSQOL v3** — Chinen, Lim, Skoglund, Gureev, O'Gorman, Hines, "ViSQOL v3: An Open Source
  Production Ready Objective Speech and Audio Metric", QoMEX 2020. arXiv:2004.09584.
  Code (Apache-2.0): <https://github.com/google/visqol>
- **PESQ** — ITU-T Rec. **P.862**; **POLQA** — ITU-T Rec. **P.863** (speech/telephony quality).
- **STOI / ESTOI** — short-time objective *intelligibility* (Taal et al. 2011; Jensen & Taal 2016).
- **No-reference (no clean reference needed):** **NISQA** (Mittag et al., 2021),
  **DNSMOS** (Reddy et al., ICASSP 2021), ITU-T Rec. **P.563**.

## Tier 3 — Learned / distributional metrics

- **Fréchet Audio Distance (FAD)** — Kilgour, Zuluaga, Roblek, Sharifi, "Fréchet Audio Distance:
  A Reference-Free Metric for Evaluating Music Enhancement Algorithms", Interspeech 2019.
  Toolkit: <https://github.com/microsoft/fadtk>
- **DPAM** — Manocha et al., "A Differentiable Perceptual Audio Metric Learned from Just
  Noticeable Differences", Interspeech 2020.
- **CDPAM** — Manocha et al., "CDPAM: Contrastive Learning for Perceptual Audio Similarity",
  ICASSP 2021. arXiv:2102.05109. Project: <https://percepaudio.cs.princeton.edu/Manocha20_CDPAM/>

## ★ Most relevant to THIS cookbook (level / dynamics effects)

For deterministic effects (AGC, compression, limiting, expanding) you usually don't need a
"quality" score — you measure **what the effect is supposed to do**. These are cheap, fully
reproducible, and computable in a few lines:

- **Loudness — LUFS/LKFS:** ITU-R Rec. **BS.1770** (currently -4) defines the K-weighted, gated
  measurement algorithm. <https://www.itu.int/rec/R-REC-BS.1770>
- **EBU R128** — the practical loudness rulebook (target −23 LUFS, −1 dBTP ceiling, **LRA**
  loudness range). <https://tech.ebu.ch/docs/r/r128.pdf> · US equivalent: **ATSC A/85** (−24 LKFS).
- **True peak (dBTP)** — oversampled peak, BS.1770 Annex 2.
- **Crest factor** (peak ÷ RMS) — a compressor literally reduces this; trivial to compute.
- **Peak-to-short-term-loudness ratio (PSR/PLR)** — used in "loudness war" analyses.
- **Practical Python:** **pyloudnorm** (Steinmetz) — a clean BS.1770/EBU R128 LUFS meter.
  <https://github.com/csteinmetz1/pyloudnorm> *(uses numpy/scipy — a reference, not necessarily
  code we ship under the no-numpy rule).*

## Reproducibility framing (for a "How do we measure it?" angle)

- Tier 1 = perfectly reproducible, perception-agnostic.
- Tier 2/3 = reproducible *given inputs*, but calibrated/trained against subjective tests, so
  they inherit those tests' scope (mostly codec artifacts or speech; can mispredict on creative
  effects).
- Subjective tests persist because no single number captures "sounds good" — but for
  *characterizing what a deterministic effect does*, task-specific objective measures (crest
  factor, LUFS) are both reproducible and genuinely informative.

## Licensing / availability quick notes (for §7)

- ITU-R recommendations (BS.1770, BS.1387, BS.1534, BS.1116) are **free to download** from itu.int.
- EBU R128 is freely available from tech.ebu.ch.
- Open-source tools: ViSQOL (Apache-2.0), auraloss (Apache-2.0), pyloudnorm (MIT),
  fadtk, cdpam — check each license before reusing code.
