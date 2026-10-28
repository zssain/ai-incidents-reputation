# The Reputational Cost of AI Ethical Incidents — Complete Project Report, Methodology, Implementation Guide and Status Audit

**Author:** Zuhair Hussain · **Prepared:** 29 October 2026 · **Repository:** `Research Paper-1` (branch `master`, last commit `d8e16e8`)

**How to read this report.** Every important statement carries one of these labels:

| Label | Meaning |
|---|---|
| **[VERIFIED]** | Checked directly in the repository (file, script, or a number recomputed from repo data on 29 Oct 2026) |
| **[GUIDE]** | Taken from `Research_Guide_and_Proposal.pdf` (16 Sep 2026), the project's design document |
| **[PAPER]** | From one of the six full-text papers as summarised in the Guide |
| **[PROPOSAL]** | A planned design choice that has **not** been executed |
| **[HYPOTHESIS]** | A prediction that needs an experiment |
| **[SUGGESTION]** | My recommended improvement, separate from the Guide's design |
| **[VERIFY]** | An external fact you must check before citing |

**Nothing in this report is an experimental result unless it is labelled [VERIFIED].** No abnormal returns, early-warning scores, or harm-type effects have been computed yet.

---

## Contents

1. Abstract and project introduction
2. Dataset analysis
3. Literature review and research gap
4. Proposed methodology (stage by stage)
5. System architecture and technology stack
6. Implementation guide (Phases 1–8)
7. Execution status audit
8. Findings: verified, expected, hypotheses, negative
9. Experimental design and evaluation strategy
10. Limitations, challenges, improvements
11. Plan of action
12. Writing the paper and defending it

---

# PART 1 — ABSTRACT AND COMPLETE PROJECT INTRODUCTION

## 1.1 Abstract

Organisations increasingly deploy AI systems that can discriminate, violate privacy, mislead, or physically harm people, and regulators now expect continuous post-deployment monitoring. Prior research has developed tools that monitor fairness drift *inside* models and has shown that social-media spikes of ESG-related discussion are associated with negative abnormal stock returns, but these two streams remain disconnected, and large-sample evidence on the *consequences* of AI ethical incidents for the firms involved is scarce. It is also unknown whether public signals anticipate such incidents before they are disclosed. This study links the AI Incident Database (AIID; snapshot of 21 September 2026, 1,689 incidents) to U.S.-listed firms through a rule-based entity matcher and a frozen, three-version coding manual, producing a screened sample of **244 incident–firm events at 47 firms (240 with high-confidence event dates)** after mechanical filters for price history, overlapping events, and earnings-announcement contamination. Using this sample, the study will (i) estimate standardized cumulative abnormal returns around disclosure with a market-model event study and clustering-robust tests, (ii) compare reactions across six AI harm types coded under a frozen codebook, (iii) measure abnormal news attention and tone, and (iv) test, under rolling-origin and leakage-controlled evaluation, whether an AI-harm-topic CUSUM detector raises alarms at least one trading day before disclosure more often than random, generic-news, spike-detection, and state-space baselines at a fixed budget of one false alarm per firm-year. The sample-construction stage is complete; the return, news, and early-warning analyses have not yet been run, so no results are claimed. The expected contribution is (1) evidence on whether, and which, AI ethical failures carry measurable short-term market and media costs, (2) a reusable, pre-registered protocol for evaluating pre-disclosure early warning, and (3) an evidence-based statement of what external monitoring can and cannot anticipate, which defines what a future internal-monitoring study would need to show.

## 1.2 Background

Three facts motivate the project.

1. **AI systems fail ethically after deployment.** Fairness metrics drift over time on real data: FEAMOE shows that models trained on older HMDA mortgage years become less accurate and less fair on later years [PAPER P5]. FairCanary shows a label-free metric (QDD) can detect an injected group-specific bug [PAPER P6].
2. **Public reputational signals move markets.** Nicolas et al. find that negative ESG-related tweet spikes (665 events, S&P 100, 2016–2022) are followed by significantly negative standardized abnormal returns (SCAAR[−1,0] = −0.289, t = −5.27), concentrated in Social and Governance topics [PAPER P4].
3. **AI incidents are now systematically recorded.** The AI Incident Database (AIID) records dated incidents, linked news reports, and named developer/deployer entities.

## 1.3 The original idea and why it was modified

**Original idea:** *internal* AI ethical-risk signals (fairness drift, monitoring alerts) → early warning → *external* reputation damage.

**Why it cannot be tested [GUIDE Part 6]:** no public dataset contains internal AI-monitoring telemetry for named companies alongside dated reputational outcomes. Companies rarely self-report failures. A simulation would assume the link it claims to find.

**Analogy.** You want to prove a dashboard warning light comes on before a car crashes, but carmakers don't publish dashboard recordings. What you *can* study is what happens after crashes become public, and whether any public warning signs existed before.

**Modified study [GUIDE Part 8, Option B + bounded Option C]:** measure the market and media consequences of publicly reported AI ethical incidents, by harm type, and test whether public news signals warn before disclosure.

## 1.4 Problem statement

There is little large-sample evidence on whether AI ethical failures at listed firms carry measurable reputational consequences, whether those consequences differ by type of harm, or whether they can be anticipated from public signals. Existing work covers ESG discussion spikes [P4], data breaches [Sinanaj et al., abstract only], and in-model fairness monitoring [P5, P6], but it does not connect AI ethical incidents to market and media outcomes at scale with confound controls.

## 1.5 Research questions and hypotheses [GUIDE Part 9]

| ID | Question | Status |
|---|---|---|
| **RQ1 (primary, confirmatory)** | Are publicly disclosed AI ethical incidents involving listed firms followed by significantly negative abnormal stock returns in the [−1, +1] trading-day window? | Data ready; analysis not run |
| RQ2 (exploratory) | Does the abnormal return differ across harm types (SAFE, FAIR, PRIV, DECEPT, SEC, ACCT)? | Codebook frozen; coding not run |
| RQ3 | Is disclosure accompanied by abnormal news attention and negative tone, and does market reaction scale with attention? | News data not collected |
| RQ4 (early warning) | Using only pre-disclosure information, does an AI-harm-topic detector alarm ≥ 1 trading day before disclosure more often than baselines and chance, at ≤ 1 false alarm per firm-year? | News data not collected |
| RQ5 (timing) | Do abnormal returns appear before disclosure (pre-event drift)? | Data ready; analysis not run |

**Hypotheses.**
- H0 (RQ1): mean SCAR[−1,+1] = 0. H1: mean SCAR[−1,+1] < 0 (one-sided).
- H0 (RQ4): early recall of the topic-specific detector ≤ generic detector and ≤ placebo. H1: it exceeds both.

## 1.6 Objectives and scope

**In scope:** U.S.-listed firms (including U.S.-listed ADRs) whose *own* AI system was involved in an AIID incident (manual "Type 1"); daily stock returns; one news source; incidents with event dates allowing 250 trading days of prior history.

**Out of scope:** private firms (OpenAI, Anthropic, ByteDance, X, etc. are explicitly blocked in `step2_listed.py`); internal AI telemetry; causal claims; social-media data; dashboards or apps (the Guide's Part 24 says "Do NOT build yet").

## 1.7 How this differs from prior work [GUIDE Part 9, INFERENCE]

| Compared with | Difference |
|---|---|
| P4 (Nicolas et al.) | Events come from curated AI-incident records, not keyword spikes; AI-specific harm taxonomy; explicit early-warning test with a false-alarm budget |
| Sinanaj et al. (data breaches) | AI harms beyond breaches; market + attention outcomes; pre-disclosure test |
| Five-firm AI-incident study (Finance Research Letters, 2024) [VERIFY — not yet read] | Many more firms; earnings exclusion; clustering-robust statistics; harm-type heterogeneity |
| P5/P6 | Studies consequences of AI failures, not detection inside a model |

**Honest novelty statement.** This is a **new application and combination** of established methods (event study + CUSUM detection + leakage-controlled evaluation) to a new event type with a new harm taxonomy. It is not a new algorithm. The novelty claim is provisional until the systematic literature search (Plan task A3) is done. Studies of AI incidents and stock returns may have appeared in 2024–2026 that the Guide did not cover.

## 1.8 A worked example (illustrative, not a result)

Take AIID incident **#6, Microsoft's Tay chatbot** posting racist content (March 2016). *Note: #6 is an Appendix-A worked example in the manual and is excluded from κ, but it illustrates the flow.*

1. **Matching:** AIID lists Microsoft as developer/deployer → alias map `"microsoft" → MSFT (direct)`.
2. **Screening:** manual §7.3 → Type 1 (own chatbot; users prompting it doesn't make it Type 2); `correct_ticker = Y`; `keep = Y`.
3. **Event date T:** the earliest linked report's publication date, rolled forward to the next trading day if it falls on a weekend.
4. **Filters:** ≥ 250 trading days of MSFT history before T ✓; no other MSFT event within ±10 trading days; no 8-K Item 2.02 earnings release within ±5 trading days.
5. **Harm code:** FAIR (discriminatory/stereotyped output) or DECEPT; the codebook's priority rule decides.
6. **Event study:** fit `R_MSFT = α + β·R_market` on days T−250…T−31, compute abnormal returns for T−1, T, T+1, sum them into CAR[−1,+1], and standardize.
7. **Early warning:** did AI-harm-topic news about Microsoft build up in T−10…T−1 enough to trigger the CUSUM alarm, using only data available on each day?

Across ~240 such events, the average standardized CAR answers RQ1, and the share of events with an early alarm (at a fixed false-alarm rate) answers RQ4.

---

# PART 2 — DATASET ANALYSIS AND UNDERSTANDING

## 2.1 Overview

| # | Dataset | Role | Status |
|---|---|---|---|
| D1 | AI Incident Database export (21 Sep 2026) | Event labels, entities, report dates | **[VERIFIED] acquired, processed** |
| D1b | AIID GraphQL API report metadata | Earliest report date, URL, source domain | **[VERIFIED] cached** (`build/report_dates_cache.json`) |
| D2 | SEC EDGAR `company_tickers.json`, `submissions/`, `companyfacts/` | Ticker universe; earnings-announcement dates | **[VERIFIED] downloaded** (982,130 submissions files; gitignored) |
| D3 | Yahoo Finance adjusted daily closes (via `yfinance`) | Stock returns | **[VERIFIED] stocks done; market index missing** |
| D4 | News attention and tone (source TBD) | RQ3, RQ4 signals | **Planned — not chosen** |
| D5 | Controls: market cap, sector, matched control firms, index membership | Confounders, placebo, false-alarm denominators | **Planned** |
| D6 | Alternative incident DB (OECD AIM or AIAAIC) | Robustness | **Planned (nice-to-have)** |
| D7 | Harm-type codes (AI coder + human check) | RQ2 | **Inputs ready; not coded** |

Datasets used by the reviewed papers (HMDA, Adult, COMPAS, FairCanary generator, Penta Group, the S&P 100 tweet corpus, CRSP, Refinitiv, I/B/E/S) are covered in Part 3. Of these, only CRSP/I/B/E/S would substitute for D3/D2 here, and only with WRDS access.

## 2.2 D1 — AI Incident Database export

- **Source:** AI Incident Database, Responsible AI Collaborative — https://incidentdatabase.ai (paper: McGregor, S. (2021), "Preventing Repeated Real World AI Failures by Cataloging Incidents: The AI Incident Database," *AAAI* 35(17), 15458–15463). Licence for incident data: CC BY-SA 4.0 [GUIDE, EXTERNAL — **VERIFY** before release].
- **File [VERIFIED]:** `data/AIID_Excel_Export-20260921.xlsx`, five sheets:
  - `Incidents`: 1,689 incidents × 59 columns (header on row 3).
  - `Reports`: 7,791 reports.
  - `Entities`: 7,341 entities.
  - `Data Dictionary`, `Coverage Map`.
- **Key Incident columns used [VERIFIED]:**

| Column | Meaning | Used for |
|---|---|---|
| `Incident ID` | Stable integer key | Join key everywhere |
| `date` | AIID "incident date", often set in hindsight | Only to spot date oddities (manual §13) |
| `title`, `description` | Text | Coding, harm coding |
| `deployer`, `developer` | Entity name lists | **Entity matching** (`ents()` in `step2_listed.py`) |
| `harmed` | Harmed parties | Not used |
| `Risk Domain`, `Harm Domain`, `Tangible Harm`, `Protected Characteristic`, … | Editor taxonomies (MIT/CSET/GMF-style) | Not used. [SUGGESTION] use as an external check on our harm codes, never as an RQ4 feature (added after T) |

- **Report metadata (D1b) [VERIFIED]:** `step3_screening.py` queries `https://incidentdatabase.ai/api/graphql` in chunks of 40 for `reports{date_published url source_domain}`. It keeps the earliest dated report as `earliest_report_date`, `earliest_report_url` and `earliest_source`, and caches the result.
- **Structure:** one row per incident. Our unit is one incident × one listed firm.
- **Data quality issues and how they were handled [VERIFIED]:**

| Issue | Handling |
|---|---|
| Entity names vary ("YouTube", "Google", "Google Bard") | Curated alias map → listed parent (direct vs subsid) |
| Private firms collide with SEC filer names | `BLOCK_AUTO` list (OpenAI, Anthropic, xAI, Twitter, TikTok, Clearview…) |
| Firms named only in the title | Recall pass `step3b_recall.py` → 128 candidates → 10 vetted additions |
| Earliest report is not real news (arXiv, SSRN, PDF, Twitter/X, blog) or predates the incident | `date_flag` set on 95 of 510 rows (18.6%); humans verified; 75 corrected dates applied (68 high-confidence, 7 low) |
| Same real event under two IDs | `duplicate_of` field (e.g., #1528 vs #1436) |
| Same firm, clustered incidents | ±10 trading-day merge in `step4_filters.py` (79 dropped) |
| Reporting bias (only media-covered incidents enter AIID) | Not fixable. Scope statement: "publicly reported incidents" |
| Post-ChatGPT reporting surge | 119 of 244 events are on/after 30 Nov 2022 [VERIFIED]. Use a period dummy and split |

- **Splits:** the event study is not a train/test design; every event is used once. For RQ4, rolling-origin splits by calendar year (Part 4, Stage 8).
- **Leakage risks:** AIID taxonomy fields and editor notes are added *after* T, so they must never feed RQ4 detectors. The `aiid_incident_date` is set in hindsight, which is why T uses the report date.
- **Sufficiency:** the gate of ≥ 100 clean events is passed (244). Harm-type subgroups will be small (exploratory only).

## 2.3 D2 — SEC EDGAR

- **Source:** U.S. SEC EDGAR (https://www.sec.gov/edgar), public domain. Files in `data/SEC EDGAR/` (gitignored; must be re-downloaded to reproduce).
- **`company_tickers.json`:** ticker ↔ CIK ↔ company title for current SEC filers (the docstring in `step2_listed.py` says 10,419 tickers). Used for exact normalised name matching.
- **`submissions/CIK##########.json` [VERIFIED code]:** filing history. `step4_filters.py` extracts **8-K filings whose `items` include 2.02 (Results of Operations and Financial Condition)** as earnings-announcement dates. That is the right event, because the 8-K 2.02 is the release itself, not the later 10-Q/10-K.
- **Fallback [VERIFIED]:** foreign private issuers file 6-K/20-F with no 8-K 2.02, so the script falls back to `yfinance.get_earnings_dates(limit=80)`. In the final sample, 235 events use SEC 8-K and **9 use yfinance** (`earn_source` column).
- **Limitation:** `company_tickers.json` is a *current* list. Firms delisted before the download can't be matched, which is a survivorship issue. It is mitigated partly because the alias map hard-codes the key issuers.

## 2.4 D3 — Daily prices (Yahoo Finance)

- **Source:** Yahoo Finance via `yfinance` 1.7.0, `auto_adjust=True`, so `Close` is adjusted for splits and dividends (a total-return proxy).
- **File [VERIFIED]:** `build/prices_panel.pkl` (gitignored): **6,722 trading days (2000-01-03 → 2026-09-24) × 72 tickers**. A separate `build/prices.csv` (2,932 rows) is an early test with only GOOGL, MSFT, TSLA and `^GSPC`.
- **Critical gap [VERIFIED]:** the panel **does not contain a market index**. The market model cannot be estimated until one is added. [SUGGESTION] Use a total-return benchmark to match the dividend-adjusted stock series: `^SP500TR` or SPY adjusted close [VERIFY ticker availability on Yahoo]. `^GSPC` is a price index; mixing it with dividend-adjusted stock returns biases α slightly.
- **Not CRSP:** no delisting returns, no point-in-time identifiers (PERMNO), and Yahoo data can be revised. The Guide allows "a documented alternative whose terms you verify" [GUIDE Part 10]. If your university has WRDS, re-run the primary analysis on CRSP as a robustness check.
- **Coverage [VERIFIED]:** every one of the 244 final events has ≥ 250 trading days before T and ≥ 10 after, so the full planned window τ = −30…+10 is available.

## 2.5 D4 — News attention and tone (planned)

The Guide requires one timestamped news source with firm mentions and tone [GUIDE Part 10]. Options:

| Option | Access | Pros | Cons |
|---|---|---|---|
| **GDELT 2.0 Global Knowledge Graph (GKG)** — https://www.gdeltproject.org | Free; raw 15-minute files or Google BigQuery `gdelt-bq.gdeltv2.gkg` [VERIFY current table name and free-tier quota] | Daily coverage since Feb 2015; `V2Organizations`, `V2Themes`, `V2Tone` fields; timestamps | Organisation names are machine-extracted (noisy); mostly article metadata, not full text; online-news bias |
| Factiva / LexisNexis / ProQuest via library | University licence [VERIFY] | Curated, full text, deduplication | Manual or limited export; licence forbids redistribution |
| RavenPack via WRDS | Licence [VERIFY] | Firm-level entity resolution, event categories, sentiment | Expensive; may not be licensed |

[SUGGESTION] Primary: **GDELT GKG**, because it is free, timestamped, and has tone. Check its firm-name precision on a hand-coded sample of 200 articles before committing. Fallback: a library news database for incident firms only.

**Construction plan [GUIDE Part 10]:**
- Fixed query per firm: legal name + common name + ticker, written down before analysis.
- Dedupe: same title or text hash within 48 h.
- Exclusion list for false name matches (e.g., "Target" the word, "Meta" in other senses, "Apple" fruit).
- English sources only.
- Trading-day assignment with a 16:00 ET cut-off.
- History: ≥ 250 trading days before the first event in the analysis window.

## 2.6 D5 — Controls (planned)

| Variable | Source | Use |
|---|---|---|
| Market cap | Yahoo `sharesOutstanding` × price, or SEC `companyfacts` (`dei:EntityCommonStockSharesOutstanding`) — local `companyfacts/` exists (20,052 files) | log size control; control-firm matching |
| Sector | SIC code in SEC `submissions` JSON (`sic` field) | Sector fixed effects; matching |
| Prior incident count | D1, counting only incidents with report date < T | Control in RQ2; RQ4 logistic feature |
| Matched control firms | 1–3 same-SIC-2-digit firms, similar size, no AIID incident in the sample period | Placebo B; false-alarm denominator for RQ4 |
| Point-in-time index membership | Not freely available. [SUGGESTION] Drop this requirement and state it as a limitation; the sample is defined by AIID, not by an index | — |

## 2.7 D7 — Harm-type coding inputs [VERIFIED]

- `harm_input.csv`: **237 unique incidents** (`incident_id, ticker, company, title, incident_url`). These are the 244 events deduplicated to incidents, because one incident can map to several tickers. Codes are mapped back to every ticker sharing the incident.
- `harm_batch_1..5.csv`: 48 / 48 / 47 / 47 / 47 rows.
- `harm_check_input.csv`: 25 rows, ticker-stratified, seed 21, for a blind human check.
- `harm_codebook_v1.md`: frozen. Six codes plus decision rules (Part 4, Stage 4).
- **No harm codes exist yet.**

## 2.8 Class imbalance, sampling bias, sufficiency

- **Event concentration [VERIFIED]:** GOOGL 59, META 50, AMZN 26, TSLA 23, MSFT 16. The **top 2 firms = 44.7%** and **top 5 = 71.3%** of the 244 events. The effective sample size for RQ1 is therefore much smaller than 244, so firm-clustered inference and leave-top-firms-out tests are essential.
- **Time distribution [VERIFIED]:** 13 events before 2016 (back to 2004), 231 from 2016 onward, and 119 after 30 Nov 2022. The Guide proposed 2016 onward [GUIDE Part 10]. [SUGGESTION] Keep 2016+ as the primary sample (news coverage begins in 2015 for GDELT) and show the full sample as robustness.
- **Weekend event dates [VERIFIED]:** 30 events have T on Saturday or Sunday and must roll to the next trading day. `step4_filters.py` already does this implicitly via `searchsorted`.
- **RQ4 imbalance:** disclosure days are rare among firm-days (on the order of a few hundred positive days among hundreds of thousands of firm-days), so accuracy and ROC-AUC are misleading. Use early recall at a fixed false-alarm budget and PR-AUC.
- **Is more data needed?**
  - News data: yes (D4).
  - Controls: yes (D5).
  - Harm annotations: yes (D7).
  - No synthetic data or augmentation. Synthetic data would undermine the empirical claims.

## 2.9 How the datasets complement each other

```
D1 AIID ──(entity match + coding)──► events (firm, T, harm type)
                                          │
D2 SEC ──► earnings dates ──(exclusion)───┤
D3 prices ──► abnormal returns ◄──────────┤  RQ1, RQ2, RQ5
D4 news ──► attention/tone, topic signals ◄┤  RQ3, RQ4
D5 controls ──► size, sector, placebo firms┘
```

---

# PART 3 — LITERATURE REVIEW AND RESEARCH GAP

Source: Parts 2–4 of the Guide, which read six full-text papers. Abstract-only sources are flagged.

## 3.1 Paper-by-paper

### P1 — Bacelar (2021), "Monitoring bias and fairness in machine learning models: A review" (preprint)
- **Problem:** organise knowledge on bias sources, fairness metrics, mitigation.
- **Method:** narrative review, with no search protocol.
- **Content:**
  - Four bias sources: institutional, individual, sample, algorithm-development.
  - Pre-, in- and post-processing mitigation.
  - Parity, confusion-matrix and calibration metrics.
- **Data / metrics / results:** none.
- **Limitations:** despite the title, it contains no monitoring method. The FOR/FDR formulas are swapped. Some citations don't support their claims.
- **Use for us:** vocabulary only. Memory hook: "the glossary, not the monitor."

### P2 — Pikatza-Gorrotxategi et al. (2022), "News versus Corporate Reputation"
- **Method:** VADER and Hu & Liu lexicon sentiment on 7,832 news items (reported) for 9 Euro Stoxx 50 firms in 2016 and 2019; compare the up/down direction with operating profit.
- **Finding:** 7/9 directions match, which the authors call a "78% correlation".
- **Limitations:**
  - No statistical test: P(≥7/9 | coin flip) ≈ 0.09.
  - Firms chosen with 2021 information (look-ahead selection).
  - Arithmetic and table inconsistencies.
  - Causal wording is unsupported.
- **Use:** a cautionary example. VADER is a transparent baseline tone tool.

### P3 — Mitic (2024), "Is Positive Sentiment Missing in Corporate Reputation?"
- **Data:** Penta Group daily reputation series (proprietary), 261 organisations × 730 days, Q3 2021–Q3 2023.
- **Method:** Kalman filter / state-space model and FFBS MCMC; "missing positive sentiment" M_z defined from the upper confidence band.
- **Finding:** proposes a 4% upward correction to positive scores.
- **Limitations:**
  - The metric is positive by construction (it measures filter uncertainty).
  - The MCMC was tuned to match the Kalman result.
  - It contradicts its own Table 1, where positive days dominate.
- **Use:** the time-series framing, and Kalman smoothing as **Baseline 2b** for tone.

### P4 — Nicolas, Desroziers, Caccioli & Aste, "ESG Reputation Risk Matters" (SSRN working paper) — **the methodological template**
- **Data:** 114M tweets on S&P 100 firms (2016–2022), CRSP, Refinitiv ESG controversies, I/B/E/S earnings dates.
- **Method:**
  - ESG lexicon (3 topics, 10 categories).
  - ESD spike detection (z = 2, 250-day rolling window).
  - Filters: ≥ 10 tweets, ≥ 5% share, ≥ 5-day gaps.
  - Exclude ±5 days around earnings or controversy news.
  - Market model on [−122, −2].
  - SAAR and SCAAR with the Boehmer test.
- **Findings:** all-ESG SCAAR[−1,0] = −0.289 (t = −5.27, N = 665); Social −0.355; Governance −0.325; Environment ≈ 0. **SAAR(t−1) = −0.117 is significant:** returns move the day *before* the spike.
- **Limitations:**
  - Lexicon errors and generic governance terms.
  - No multiple-testing correction.
  - Not causal.
  - Detection rather than prediction.
  - Twitter API no longer accessible.
- **Use:** event-window design, ±5-day earnings exclusion, BMP test, ESD rule as **Baseline 2a**. The pre-event effect is a warning for RQ4.

### P5 — Sharma, Henderson & Ghosh (2022), FEAMOE
- **Method:** mixture of logistic-regression experts with a softmax gate, plus SPD, AOD and burden penalties. Online expert addition. Theorem: gate-weighted SHAP.
- **Data:** Adult, COMPAS, HMDA 2007–2017.
- **Finding:** fixed models lose accuracy *and fairness* as the training year ages on HMDA. This is real-data evidence of fairness drift.
- **Limitations:**
  - No significance tests.
  - Inconsistent protected attribute.
  - Unexplained accuracy discrepancy (79.20% vs 83.24%).
  - The proof treats input-dependent gates as constants.
- **Use:** motivation only (fairness drifts). The architecture is not needed.

### P6 — Ghosh, Shanbhag & Wilson (2022), FairCanary (AIES '22)
- **Method:** Quantile Demographic Disparity (QDD), label-free and in output units, plus QDDA feature attribution with SHAP or Integrated Gradients.
- **Data:** synthetic salary data, 20k per day × 3 days, with an injected Day-2 bug.
- **Finding:** QDD moves from $156 to −$8,677 on Day 2. SPD misses the bug; DI catches it only at the $200k threshold.
- **Limitations:**
  - The case study uses one bin (so QDD reduces to a mean difference).
  - One abrupt synthetic shock.
  - No detection-delay or false-alarm analysis.
- **Use:** motivation for internal monitoring as future work. Its missing delay/false-alarm evaluation is exactly what our RQ4 protocol supplies on the *external* side.

### Abstract-only sources (Stream C) [GUIDE Part 4]
- De Miguel Velázquez et al. (2024): 639 AIID incidents analysed. Shows AIID is research-grade.
- Raghupathi, Ren & Kulkarni (2026): 3,494 OECD AIM records. Reporting rose 4.6× after ChatGPT.
- Hadan et al. (2025): 202 incidents. Developers rarely self-report.
- Abraham et al. (2026): incident counts ≠ risk.
- Sinanaj et al. (2015): data breaches → social-media reputation decline. The closest precedent.
- Five-firm AI-incident event study (Finance Research Letters, 2024) [EXTERNAL — **must be read and cited; authors not verified here**].

## 3.2 Comparative table

| Paper | Problem | Data | Real/Synth | Temporal | Method | Key metric | Main finding | Main weakness | Relevance |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Bias/fairness overview | None | — | No | Narrative review | Definitions | Re-evaluate models periodically | No method/data | Low |
| P2 | Reputation via news | 7,832 news, 9 firms | Real | 2 years | Lexicon sentiment | Direction match | 7/9 match | No test; selection | Low (cautionary) |
| P3 | Negativity bias | Penta, 261 orgs × 730 d | Real (proprietary) | Daily | Kalman, FFBS | M_z | +4% correction | Positive by construction | Medium |
| P4 | ESG reputation → returns | 114M tweets, CRSP | Real | Daily | ESD + event study | SAAR/SCAAR | −0.289 SCAAR | Pre-event effect; lexicon | **High** |
| P5 | Fair adaptive model | Adult, COMPAS, HMDA | Real + synth | Annual | Fair MoE | Acc, SPD, AOD | Fairness drifts | No tests | Medium |
| P6 | Label-free fairness monitor | Synthetic salary | Synth | 3 days | QDD + QDDA | QDD ($) | Catches injected bug | 1 bin, 1 shock | Medium (future work) |

## 3.3 The research gap

**What is established:**
- Fairness drifts and can be monitored in the lab [P5, P6].
- Public ESG signal spikes are associated with negative returns [P4].
- Data breaches hurt social-media reputation [Sinanaj].
- AI incidents are catalogued at scale [AIID, OECD AIM].

**What is missing (Guide gaps G3 + G4):**
1. **G3:** a large-sample, confound-controlled event study of AI ethical incidents with a harm-type breakdown.
2. **G4:** a formal, leakage-controlled test of whether public signals warn before AI-incident disclosure at a controlled false-alarm rate.

**What we do NOT claim to fill:** G1 (internal signals → external reputation) is untestable with public data. It stays as future work.

**Type of contribution:** a new application plus a protocol (combination of existing methods), not a new algorithm. If the five-firm study or a newer paper already did a large-sample AIID event study, the contribution becomes the harm-type heterogeneity, the coding protocol and the early-warning test. The systematic search must settle this.

---

# PART 4 — COMPLETE PROPOSED METHODOLOGY

## 4.1 Flowchart (with implementation status)

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ S1  DATA COLLECTION      AIID export · AIID GraphQL report dates ·      │ ✅ done
 │                          SEC EDGAR · Yahoo prices                        │ ⚠ index missing
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S2  ENTITY MATCHING      deployer/developer → listed parent ticker      │ ✅ done
 │                          (alias map + exact SEC match + recall pass)    │
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S3  SCREENING & CODING   manual v3: correct_ticker, type 1/2/3,          │ ✅ done
 │                          duplicates, date correction, keep; κ; adjudic. │ ⚠ validation 30/50
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S4  HARM-TYPE CODING     6 codes, AI coder + blind human check (25)      │ ⏳ inputs ready
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S5  EVENT FILTERS        pre/post history · ±10td merge · ±5td earnings │ ✅ done (N=244)
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S6  PRE-REGISTRATION     RQ1 window, RQ4 B/W/h, detectors, tests (OSF)  │ ⏳ not started
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S7  EVENT STUDY          market model [T−250,T−31] · AR/CAR · BMP+KP    │ ⏳ not started
 │                          · sign/Wilcoxon · placebos · harm regression   │
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S8  NEWS PANEL           firm×day counts/tone · AI-harm topic signals   │ ⏳ not started
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S9  EARLY WARNING        baselines 0–2 · CUSUM · rolling-origin eval    │ ⏳ not started
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S10 ROBUSTNESS/PLACEBO   windows · dates ±1 · top-5 out · periods · alt │ ⏳ not started
 ├─────────────────────────────────────────────────────────────────────────┤
 │ S11 INTERPRETATION       associations only · what external monitoring   │ ⏳
 │                          can / cannot anticipate                        │
 └─────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Stage S1 — Data collection ✅ (index ⚠)

**Conceptual.** Gather the raw ingredients: the list of AI incidents, when each was first reported, which listed company it concerns, its stock prices, and its earnings dates.

**Technical [VERIFIED].**
- AIID: Excel export, frozen and dated (20260921). The file name records the snapshot.
- Report dates: GraphQL query `incidents(filter:{incident_id:{IN:[…]}}){ incident_id date title reports{ date_published url source_domain } }`, with retries and a JSON cache.
- Prices: `yf.download(tickers, start="2000-01-01", end="2026-09-25", auto_adjust=True)`, cached to `prices_panel.pkl`.
- SEC: bulk `submissions` and `companyfacts` downloads.

**Output:** raw files in `data/` and caches in `build/`.

**Problems:** the API or Yahoo can change, and data can be revised. **Mitigation:** caches plus the snapshot date. [SUGGESTION] Record SHA-256 hashes of `prices_panel.pkl` and the AIID export in a `DATA_MANIFEST.md`.

**Validation:** row counts and a spot-check of 10 report dates against the AIID website.

**To do:** add the market index (see Phase 2).

## 4.3 Stage S2 — Entity matching ✅

**Conceptual.** AIID says "YouTube" or "Waymo", but the stock that trades is Alphabet (GOOGL). This stage translates every AI developer/deployer name into the listed parent's ticker, and refuses to match private firms that happen to share a name with an SEC filer.

**Technical [VERIFIED, `step2_listed.py`].**
1. `ents(row)`: split `deployer` and `developer` on `,`/`;`, strip and lowercase → a set of entity names.
2. `match(name)`, in priority order:
   - (a) `ALIASES` lookup → `(ticker, "direct"|"subsid")`. ~45 curated entries, e.g. `youtube→GOOGL subsid`, `cruise→GM subsid`, `acclarent→JNJ subsid`, `navihealth→UNH subsid`.
   - (b) if the name is in `BLOCK_AUTO` → no match.
   - (c) normalise (lowercase, strip SEC suffixes like `/de/`, remove punctuation, drop tokens such as inc/corp/holdings/class) and look up an **exact** normalised SEC title.
3. A per-incident ticker set where `direct` beats `subsid`.
4. Counts: STRICT (≥ 1 direct entity) vs LENIENT (includes subsidiaries).

**Why exact matching rather than fuzzy:** precision matters more than recall here, because a wrong firm means a wrong stock. The recall loss is recovered by the curated alias list and a separate title-based recall pass (`step3b_recall.py` → `build/recall_candidates.csv`, 127 candidates → 10 hand-vetted additions such as `#225 IBM Watson for Oncology` and `#428 HSBC voice-ID`).

**Output:** `build/listed_company_incidents.csv` (71 tickers) and the (incident, ticker) pairs that feed S3.

**Problems:**
- Subsidiaries sold before the event (J&J/Acclarent: caught in adjudication, rows #1436/#1528 JNJ set to N).
- ADRs of foreign firms (BABA, BIDU, XPEV).
- Name collisions (Target, Meta).

**Validation:** two-coder `correct_ticker` judgement. Validation agreement on `correct_ticker` = **100% (κ = 1.0, n = 30)** [VERIFIED, recomputed].

## 4.4 Stage S3 — Screening and coding ✅ (⚠ validation)

**Conceptual.** Not every matched pair is an event we want. We keep only cases where *the firm's own AI* went wrong, because only then should the market attribute the incident to that firm. Studies that test many firms at once (Type 3) and outsiders misusing a firm's tool (Type 2) are excluded from the main sample.

**Technical [VERIFIED].**
- `step3_screening.py` builds `build/screening_sheet.csv/.xlsx`: **510 (incident, ticker) rows from 460 incidents** (500 primary + 10 recall). It adds the date-quality flags and a seeded (42), ticker-stratified 50-row pilot (largest-remainder allocation).
- Coding fields (manual v3):

| Field | Rule |
|---|---|
| `correct_ticker` Y/N | Did this firm build/operate/deploy/own the AI? Not about blame (§6) |
| `responsibility_type` 1/2/3 | Ask Type 3 first (multi-company study / no-event paper), then Type 2 (identifiable outside actor used the tool in *their own* harmful operation), else Type 1 (§7–§11) |
| `duplicate_of` | Lower ID if same real-world event (§12) |
| `corrected_event_date` | Only if `date_flag` set and the date is wrong; earliest real news article (§13) |
| `keep` | Mechanical: Y iff type = 1 ∧ ticker = Y ∧ not duplicate (§14) |

- **Manual development [VERIFIED, Appendix B]:**

| Round | Coders | κ (responsibility_type) | Action |
|---|---|---|---|
| Pilot 1 | A vs B | 0.21 (manual) | → v2 (Rules 1–5) |
| Pilot 2 | A vs B | 0.27 (manual); 0.286 recomputed (76% agreement, n = 25) | → v2 |
| Pilot 3 | A vs B (human) | −0.14 (manual); −0.136 recomputed (68%, n = 25) | → v3 rewrite: decision tree, UNCERTAIN flag, AI-coder procedure |

- **Main coding:** an AI coder ("Astra" in the files) coded 410 rows under `coderB_prompt_v3.txt` in 8 batches plus a retry batch (`astra_out_*.csv` → `astra_all.csv`).
- **Human validation [VERIFIED, recomputed today without modifying files]:** `validation_input.csv` drew 50 rows, but `validation_coderB_human.csv` has **30** coded rows. None are Appendix-A incidents.

| Field | κ | Raw agreement | PABAK | n |
|---|---|---|---|---|
| responsibility_type | **−0.042** | 83% | 0.75 | 30 |
| correct_ticker | 1.000 | 100% | 1.00 | 30 |
| keep | 0.268 | 87% | 0.73 | 30 |

Crosstab of `responsibility_type` (rows = AI, columns = human): AI 1 / human 1 = 25; AI 1 / human 2 = 3; AI 3 / human 1 = 2.

**Why κ is negative despite 83% agreement (the "kappa paradox", Feinstein & Cicchetti 1990):** κ = (p_o − p_e)/(1 − p_e). Both coders label ~90% of rows Type 1, so chance agreement is p_e = (28/30)(27/30) = 0.84, slightly *above* observed agreement p_o = 0.833. That makes κ = (0.833 − 0.84)/0.16 ≈ −0.04. PABAK (Byrt, Bishop & Carlin 1993) adjusts for this prevalence and gives 0.75.

**This misses the manual's own target (κ ≥ 0.6) and its required sample (≥ 50). You must report it honestly** (manual §19.4 says "Report the result honestly whatever it is") and should code the remaining 20 validation rows. See Part 10.

- **Adjudication [VERIFIED]:**
  - All 5 type disagreements were settled in the AI coder's favour, with written reasons (`adjudication_log.csv`).
  - 26 UNCERTAIN rows resolved: 24 accepted as proposed and 4 changed (#5 ISRG → Type 3/N, #1401 AMZN → Type 2/N, #400 GOOGL → Type 3/N, #92 AAPL stays N).
  - J&J divestiture handled.
  - 75 date corrections.
- **Final labels [VERIFIED, `build/screening_final.csv`]:** Type 1 = 413, Type 2 = 26, Type 3 = 71; `correct_ticker` N = 19; **keep = Y: 399**.

**Problems:**
- The adjudicator (lead author) also designed the rules, and every type disagreement went the AI's way. Disclose this.
- The AI coder's model name, version and run date are **not recorded** in the repo, although manual §19 requires them. Add them.

**Validation:** κ, PABAK and raw agreement as above. All adjudications logged.

## 4.5 Stage S4 — Harm-type coding ⏳

**Conceptual.** Is the harm about safety, discrimination, privacy, deception, security, or accountability? Different harms may cost different amounts (P4 found Social and Governance mattered and Environment didn't).

**Codebook [VERIFIED, `harm_codebook_v1.md`, frozen].**
- Fields: `harm_primary` ∈ {SAFE, FAIR, PRIV, DECEPT, SEC, ACCT}, optional `harm_secondary`, and a one-sentence `reason`.
- Decision rules:
  1. Code the harm the headline and first reports emphasise.
  2. Tie-break priority: SAFE > FAIR > PRIV > SEC > DECEPT > ACCT.
  3. Wrongful removals → ACCT unless biased against a protected group (→ FAIR).
  4. Failure to remove harmful content → code the content's harm.
  5. Privacy leak through a security flaw → PRIV if personal data was exposed.
  6. `UNCERTAIN:` prefix when unsure.

**Procedure (planned):**
1. The AI coder codes 237 incidents with a fixed prompt. Record the model and date.
2. The author blind-codes `harm_check_input.csv` (25).
3. Report raw %, Cohen's κ, PABAK.
4. Adjudicate disagreements and UNCERTAIN rows.
5. Map codes back to the 244 events.
6. **All of this happens before any returns are computed.**

**Mapping to the Guide's six categories:** SAFE = safety, FAIR = discrimination/bias, PRIV = privacy, DECEPT = deception/misinformation, SEC = security/misuse, ACCT = accountability/transparency.

**Risk:** with 25 check items and an uneven distribution, κ will be unstable (same paradox as S3). [SUGGESTION] Raise the check to 50, stratified by AI-assigned code, and report a 95% bootstrap CI for κ.

**Leakage rule:** harm type is **never** a feature in RQ4 detectors [GUIDE Part 13].

## 4.6 Stage S5 — Event filters ✅

**Conceptual.** Remove events where something else would contaminate the stock reaction: too little price history to know "normal" behaviour, two incidents back to back, or an earnings announcement nearby.

**Technical [VERIFIED, `step4_filters.py`, config `PRE, POST, MERGE, EARN = 250, 5, 10, 5`].**
1. `event_date` = `corrected_event_date` if present, else `earliest_report_date`.
2. Listing/history: ≥ 250 trading days before T and ≥ 5 after.
3. Same-ticker merge: walk events in date order; drop any event within ≤ 10 trading days of the last *kept* event, so the earliest survives.
4. Earnings blackout: drop if any 8-K 2.02 date (or yfinance fallback) is within ±5 trading days of T. If fallback coverage doesn't reach back to the event, mark `earn_source = none` (no blackout applied).

**Attrition funnel [VERIFIED]:**

```
AIID incidents                                     1,689
Screened (incident, ticker) rows                     510   (460 incidents)
keep = Y after coding + adjudication                 399
  − insufficient pre-history (<250 td)               −21   (IPOs after event: UBER×7, KSCP×3, ABNB, …)
  − insufficient post-history                         −1   (GOOGL 2026-09-18)
  − merged with prior same-firm event (≤10 td)       −79
  − earnings within ±5 td                            −54
Final events                                         244   (237 incidents, 47 firms)
  of which high-confidence dates                     240   (4 events with low-confidence corrected dates excluded)
```

**Note:** `POST = 5`, but the Guide's windows extend to τ = +10. All 244 events already have ≥ 10 post days [VERIFIED], so nothing changes now. Still set `POST = 10` so a re-run stays consistent with the paper.

**Note on the merge:** the merge runs *before* the earnings filter. If the earliest event of a cluster is then dropped for earnings, the later (merged) incident is lost too. This is defensible (the cluster is contaminated) but should be stated.

**Validation:** `build/drop_log.csv` logs every drop with its reason.

## 4.7 Stage S6 — Pre-registration ⏳

Register on OSF before merging returns with events [GUIDE Part 16]:
- RQ1 window [−1,+1], one-sided.
- Estimation window [T−250, T−31].
- BMP + Kolari–Pynnönen test; α = 0.05.
- Primary sample: high-confidence, 2016+ (or the full 244; decide *now*).
- RQ4: B = 1, W = 10, L = 2, h = 5.
- Detector list.
- BH correction for RQ2.
- Everything else labelled exploratory.

**Why:** it prevents choosing windows after seeing results, the most common criticism of event studies. **Status:** no pre-registration file found in the repo [VERIFIED].

## 4.8 Stage S7 — Event study ⏳

**Conceptual.** Each stock has a "normal" relationship with the market (it tends to rise 1.2% when the market rises 1%). We learn that relationship on a quiet period well before the incident, then look at how far the stock departs from it around the incident. Averaging the departures over ~240 events cancels out unrelated noise. What remains is the typical reaction.

**Technical.**

*Market model* (MacKinlay 1997), estimated by OLS on the estimation window E = [T−250, T−31] (L = 220 days):

$$R_{i,t} = \alpha_i + \beta_i R_{m,t} + \varepsilon_{i,t}, \qquad \hat\sigma_i^2 = \frac{1}{L-2}\sum_{t\in E}\hat\varepsilon_{i,t}^2$$

*Abnormal return* for τ ∈ [−30, +10]: $AR_{i,\tau} = R_{i,\tau} - \hat\alpha_i - \hat\beta_i R_{m,\tau}$

*Standardized AR* (with prediction-error correction):

$$SAR_{i,\tau} = \frac{AR_{i,\tau}}{\hat\sigma_i\sqrt{1 + \frac1L + \frac{(R_{m,\tau}-\bar R_m)^2}{\sum_{t\in E}(R_{m,t}-\bar R_m)^2}}}$$

*Cumulative:* $CAR_i[\tau_1,\tau_2] = \sum_{\tau=\tau_1}^{\tau_2} AR_{i,\tau}$, $\quad SCAR_i = CAR_i / (\hat\sigma_i\sqrt{\tau_2-\tau_1+1})$

*BMP test* (Boehmer, Musumeci & Poulsen 1991): $t_{BMP} = \frac{\overline{SCAR}\sqrt N}{s(SCAR)}$, where s is the cross-sectional SD. It is robust to event-induced variance.

*Kolari–Pynnönen (2010) adjustment* for cross-correlation when events cluster in calendar time: $t_{KP} = t_{BMP}\sqrt{\frac{1-\bar r}{1+(N-1)\bar r}}$, where $\bar r$ is the mean pairwise correlation of estimation-window residuals across events. [SUGGESTION] Because 71% of events are at 5 firms, also report a **firm-clustered** test: regress SCAR on a constant with firm-clustered SEs.

*Non-parametric checks:*
- Generalized sign test (Cowan 1992): $Z = \frac{w - N\hat p}{\sqrt{N\hat p(1-\hat p)}}$, where w = number of negative CARs and $\hat p$ = estimation-period share of negative ARs.
- Wilcoxon signed-rank test on SCAR.

*Windows:*

| Window | Purpose |
|---|---|
| [−1,+1] | Primary |
| [0,+1], [0,+5] | Secondary |
| [−5,−2], [−21,−2] | Pre-event (RQ5) |
| [−122,−2] estimation | Robustness (P4) |

*Placebos:*
- A: same firm, random non-event dates. Exclude ±30 days around any real event; 1,000 draws.
- B: same dates at matched control firms.

*RQ2 regression:*

$$CAR_i[-1,+1] = \sum_h \gamma_h \mathbb 1[\text{harm}_i = h] + \delta_1\log MCap_i + \delta_2 \text{Post2022}_i + \delta_3 \text{PriorInc}_i + \text{SectorFE} + \text{YearFE} + u_i$$

Use firm-clustered SEs and Benjamini–Hochberg (1995) q-values across harm coefficients.

**Why this method:** event studies are the standard way to measure information effects on prices. P4 used exactly this design, so results are comparable. Alternatives such as Fama–French 3-factor or market-adjusted returns go in robustness. Over [−1,+1], model choice matters little for large firms.

**Outputs:** `build/event_ar.parquet` (event × τ), `build/event_car.csv` (event × window), result tables, CAAR plot.

**Problems:** thin trading (not an issue for these large caps); ADR time zones (BABA, BIDU, XPEV trade on news from Asian hours → T vs T+1 ambiguity, covered by [−1,+1]); overlapping events across firms on the same date (KP adjustment).

**Validation:**
- Unit-test the AR code on a synthetic stock = 1.2 × market + noise with an injected −3% shock. The code must recover β ≈ 1.2 and AR ≈ −3%.
- Placebo distribution centred on 0.
- Reproduce P4's sign of effect on a toy set (optional).

## 4.9 Stage S8 — News panel ⏳

**Conceptual.** Count, for each firm and trading day, how many articles mention it and how negative they are, both overall ("generic") and for articles about AI harms ("topic"). Express each count relative to that firm's own past year, so a normal day for Google (hundreds of articles) and a normal day for Knightscope (a few) are comparable.

**Technical.**
- Assign each article to trading day d(t): timestamp ≤ 16:00 ET → that day if it is a trading day; otherwise the next trading day.
- Generic volume $V_{i,d}$ and mean tone $\tau_{i,d}$.
- Topic volume $V^{(k)}_{i,d}$ for harm lexicon k ∈ {SAFE, …, ACCT} and for a pooled AI-harm lexicon. The lexicon is built **only from training-year articles** (e.g., top terms by log-odds ratio between pre-incident-window articles and other articles, plus seed terms like "bias", "discriminat*", "privacy", "facial recognition", "hallucinat*", "deepfake", "autopilot crash", "jailbreak").
- Past-only standardization:

$$z_{i,d} = \frac{x_{i,d} - \mu_{i,[d-250,d-1]}}{\sigma_{i,[d-250,d-1]}}$$

Note the window ends at d−1, so it never includes today.

**Leakage traps:** don't use `rolling()` without `.shift(1)`; don't fit the lexicon on all years; don't use an LLM trained after the period to score pre-event news [GUIDE Part 13].

**Validation:**
- Hand-check 200 matched articles for firm-mention precision (target ≥ 90%) [SUGGESTION].
- Confirm a visible attention spike at T for known big incidents.

## 4.10 Stage S9 — Early-warning evaluation ⏳

**Conceptual.** A smoke detector is useful only if it rings *before* the fire and doesn't ring every time you make toast. We give each detector the same "toast budget" (≤ 1 false alarm per firm per year) and ask which one rings before more incidents.

**Definitions [GUIDE Part 14]:**

| Symbol | Meaning |
|---|---|
| $T_e$ | Disclosure trading day of event e |
| $a_{i,t}$ | Alarm on day t, using data up to t |
| W | Warning window = 10 |
| L | Grace window = 2 |

- Detection time: $d_e$ = first t ∈ [T_e − W, T_e + L] with an alarm.
- Lead time: $\ell_e = T_e - d_e$.
- **Early recall:** $ER = \#\{e: \ell_e \ge 1\}/\#e$.
- False alarm: an alarm *episode* (consecutive alarm days count once) outside every [T_e − W, T_e + L] for that firm.
- Rate = false episodes / firm-years monitored, including control firms.
- Same-day detection (ℓ = 0) is **not** early warning: it is the disclosure coverage itself.

**Detectors:**

| Level | Detector |
|---|---|
| B0 | Random alarms at the proposed detector's alarm rate |
| B1 | Generic volume > firm's past-year p-th percentile |
| B2a | ESD rule (P4): $V_{i,d} > \bar V + 2\sigma$ over 250 days, ≥ 10 articles |
| B2b | Kalman-smoothed generic tone; alarm when the filtered level falls below its lower band (P3-style) |
| **Proposed** | One-sided CUSUM (Page 1954) on standardized topic volume and tone per harm type; alarm if any statistic crosses its threshold |
| Optional | L2 logistic regression for P(disclosure in (t, t+5]) |

**CUSUM:**

$$S_{i,t} = \max(0,\; S_{i,t-1} + z_{i,t} - k), \qquad \text{alarm if } S_{i,t} > h_c,\ \text{then reset } S=0$$

Here k is the allowance (typical 0.5, i.e. detecting a shift of about 1σ) and h_c is tuned on validation years to meet the budget.

**Rolling-origin protocol:** for test year Y:
1. Fit lexicon and parameters on years ≤ Y−2.
2. Choose thresholds on Y−1 so false alarms ≤ 1 per firm-year.
3. Evaluate on Y.

Repeat for Y = 2019 … 2026 [SUGGESTION: needs ≥ 3 years of news history before the first test year], then pool.

**Early-alarm audit:** manually classify every early alarm as precursor, same incident reported earlier (a date error), or unrelated. Report results both ways [GUIDE Part 14].

**Statistics:**
- Firm-block and time-block bootstrap (10,000 resamples) of ER differences.
- Wilson intervals for ER.
- Placebo: re-date events within the same firm-year 1,000×.

## 4.11 Stage S10 — Robustness and placebo ⏳ (see Part 9, Experiments 6–7)

## 4.12 Stage S11 — Interpretation

- Associations, not causes.
- Separate confirmatory (RQ1, RQ4 at pre-registered settings) from exploratory (everything else).
- Translate RQ4 into a statement of what external monitoring can and cannot anticipate.

---

# PART 5 — SYSTEM ARCHITECTURE AND TECHNOLOGY STACK

## 5.1 What kind of "system" this is

This is a **batch, file-based, reproducible research pipeline**, not a deployed service. There is no backend, API, database server, frontend, or deployment target, and the Guide explicitly recommends against building dashboards or web apps [GUIDE Part 24]. "Architecture" here means the data flow between scripts and files.

## 5.2 Architecture diagram

```
                ┌──────────────────────── EXTERNAL SOURCES ───────────────────────┐
                │ AIID Excel export   AIID GraphQL   SEC EDGAR bulk   Yahoo (yf)  │
                │                                                   News (TBD)    │
                └───────┬──────────────┬───────────────┬───────────────┬─────────┘
                        │              │               │               │
   data/ (raw, frozen)  ▼              ▼               ▼               ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ step2_listed.py ─► step3b_recall.py ─► step3_screening.py ─► screening_sheet   │ ✅
 │                                         (GraphQL cache)        (.csv/.xlsx)    │
 │      coders (AI + human) ─► astra_*.csv, validation_*.csv, adjudication_log    │ ✅
 │      step5_kappa.py ─► κ ; adjudicate ─► build/screening_final.csv             │ ✅
 │      step4_filters.py (+prices_panel.pkl, SEC 8-K) ─► final_sample*.csv        │ ✅
 ├────────────────────────────────────────────────────────────────────────────────┤
 │ harm coding ─► harm_codes.csv (+κ)                                              │ ⏳
 │ step6_returns.py   ─► event_ar.parquet, event_car.csv                           │ ⏳
 │ step7_eventstudy.py─► tables (BMP/KP/sign/Wilcoxon), placebo, RQ2 regression    │ ⏳
 │ step8_news.py      ─► news_panel.parquet (firm × trading day)                   │ ⏳
 │ step9_warning.py   ─► detector alarms, ER/FA/lead-time, bootstrap               │ ⏳
 │ step10_robust.py   ─► robustness grid                                           │ ⏳
 │ figures/ , tables/ ─► paper                                                     │ ⏳
 └────────────────────────────────────────────────────────────────────────────────┘
```

## 5.3 Storage design

| Layer | Location | Format | In git? |
|---|---|---|---|
| Raw inputs | `data/` | xlsx, json | AIID yes; SEC no (`.gitignore`) |
| Caches | `build/*.pkl`, `report_dates_cache.json` | pickle, json | pkl no; json yes |
| Coded labels | repo root + `build/screening_final.csv` | csv | yes |
| Analysis outputs (planned) | `build/`, `results/` | parquet/csv, png/pdf | csv yes; licensed news no |

[SUGGESTION] Move coder-facing files into `coding/` once coding ends. The root currently holds 50+ files. Don't move anything while coding is in progress, because the README tells coders to look only at the root.

## 5.4 Technology stack

| Technology | Role | Implemented? | Why chosen | Alternatives |
|---|---|---|---|---|
| Python 3.13 (`.venv`) | Everything | ✅ | Ecosystem, reproducibility | R (`estudy2`), Stata (`eventstudy2`) |
| pandas 3.0.6, numpy 2.5.3 | Data wrangling | ✅ | Standard | polars |
| openpyxl 3.1.5 | Coder spreadsheets with validation dropdowns | ✅ | Coders work in Excel | Google Sheets |
| requests 2.34.2 | AIID GraphQL | ✅ | Simple | gql |
| yfinance 1.7.0 | Prices, fallback earnings dates | ✅ | Free | CRSP via WRDS (preferred if available) |
| SEC EDGAR bulk JSON | Tickers, 8-K 2.02 dates | ✅ | Free, authoritative for U.S. filers | I/B/E/S |
| LLM AI coder ("Astra") | Main coding pass | ✅ (model not recorded) | Scale; manual-compliant | Second human coder |
| statsmodels | OLS, clustered SEs | ❌ not installed | Standard econometrics | linearmodels |
| scipy | Wilcoxon, distributions | ❌ not installed | Standard | — |
| pyarrow | Parquet | ❌ | Fast columnar storage | csv |
| matplotlib | Figures | ❌ | Publication plots | plotly |
| GDELT / library news | News panel | ❌ | See §2.5 | RavenPack |
| OSF | Pre-registration | ❌ | Standard | AsPredicted |

## 5.5 Security, privacy, reliability

- **Privacy:** no personal data is collected. Incident descriptions may name harmed individuals; don't republish them [GUIDE §3.12].
- **Licensing:** AIID is share-alike, so the derived linkage table should be released under CC BY-SA [VERIFY]. Licensed news and returns must not be redistributed.
- **Reliability:** caches make runs deterministic. Seeds are fixed (42 for the screening pilot, 21 for the harm check). [SUGGESTION] Add hashes and a `make all` target.
- **Scalability:** ~250 events × 41 days is trivial on a laptop. A GDELT GKG extraction is the only heavy step; use BigQuery filters, not raw downloads.

---

# PART 6 — COMPLETE IMPLEMENTATION GUIDE

> Code below is **implementation-ready guidance that has not been run**. Adjust column names to the files.

## Phase 1 — Research preparation and environment ✅ (partially)

- **Objective:** a reproducible environment.
- **Done [VERIFIED]:**
  - `.venv` with pandas, numpy, openpyxl, requests, yfinance.
  - Repo structure (`scripts/`, `build/`, `data/`).
  - README with pipeline order.
  - git history with descriptive commits.
- **To do:**
  ```bash
  .venv/bin/pip install statsmodels scipy pyarrow matplotlib
  .venv/bin/pip freeze > requirements.txt
  ```
  Add `DATA_MANIFEST.md`: AIID snapshot date, SEC download date, Yahoo download date and file hashes, AI-coder model and version.
- **Acceptance:** a fresh clone plus `pip install -r requirements.txt` re-runs `step4_filters.py` and reproduces N = 244.

## Phase 2 — Dataset acquisition and preprocessing (mostly ✅)

**Done:** S1–S5 above.

**Task 2.1 — Add the market index (critical, ~1 hour).**

```python
# scripts/add_market_index.py  (proposed)
import pandas as pd, yfinance as yf
px = pd.read_pickle("build/prices_panel.pkl")
mkt = yf.download(["^SP500TR", "^GSPC"], start="2000-01-01", end="2026-09-25",
                  auto_adjust=True, progress=False)["Close"]
px = px.join(mkt, how="left")        # same trading calendar
assert px["^SP500TR"].loc["2005":].notna().mean() > 0.99
px.to_pickle("build/prices_panel.pkl")
```

**Task 2.2 — Set `POST = 10`** in `step4_filters.py` and re-run. Confirm N stays 244.

**Task 2.3 — Decide the primary sample:** high-confidence (240) and 2016+ (≈ 227–231). Write the decision into the pre-registration.

**Task 2.4 — Controls:** SIC codes from `submissions/*.json`, market cap at T−31, prior incident counts using report dates < T.

**Task 2.5 — Matched controls:** for each event firm, 3 firms with the same 2-digit SIC, closest log market cap, and no AIID listed-firm match. Draw from the SEC ticker list and download their prices.

## Phase 3 — Baseline implementation

**Event study baselines:** the zero-effect null and Placebos A/B.

**Early-warning baselines (after news data):**

```python
def past_z(x, win=250):
    mu = x.shift(1).rolling(win, min_periods=60).mean()
    sd = x.shift(1).rolling(win, min_periods=60).std()
    return (x - mu) / sd

def b1_percentile(vol, p):                # Baseline 1
    thr = vol.shift(1).rolling(250, min_periods=60).quantile(p)
    return (vol > thr).astype(int)

def b2a_esd(vol, z=2.0, min_count=10):    # Baseline 2a (P4-style)
    return ((past_z(vol) > z) & (vol >= min_count)).astype(int)

def b0_random(index, rate, rng):          # Baseline 0
    return pd.Series((rng.random(len(index)) < rate).astype(int), index=index)
```

Baseline 2b (Kalman tone): use `statsmodels.tsa.statespace.UnobservedComponents(tone, level="local level")` fitted on training years only. Alarm when the filtered level < lower 95% band of the one-step-ahead prediction.

## Phase 4 — Proposed methodology implementation

**4.1 Returns and ARs (S7):**

```python
import numpy as np, pandas as pd
EST = (-250, -31); WIN = range(-30, 11)

def event_returns(ret, mkt, T):
    """ret, mkt: daily simple returns (Series, trading-day index). T: event date."""
    idx = ret.dropna().index
    t0 = idx.searchsorted(pd.Timestamp(T))          # rolls weekends/holidays forward
    est = idx[t0 + EST[0]: t0 + EST[1] + 1]
    y, x = ret.loc[est], mkt.loc[est]
    beta = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); alpha = y.mean() - beta * x.mean()
    resid = y - alpha - beta * x; L = len(est)
    s2 = (resid ** 2).sum() / (L - 2)
    rows = []
    for tau in WIN:
        d = idx[t0 + tau]
        ar = ret.loc[d] - alpha - beta * mkt.loc[d]
        c = 1 + 1/L + (mkt.loc[d] - x.mean())**2 / ((x - x.mean())**2).sum()
        rows.append({"tau": tau, "date": d, "AR": ar, "SAR": ar / np.sqrt(s2 * c)})
    out = pd.DataFrame(rows); out.attrs.update(alpha=alpha, beta=beta, sigma=np.sqrt(s2), resid=resid)
    return out

def car(df, a, b, sigma):
    w = df[(df.tau >= a) & (df.tau <= b)]
    c = w.AR.sum(); return c, c / (sigma * np.sqrt(len(w)))
```

**4.2 Tests:**

```python
from scipy import stats
def bmp(scar):                     # Boehmer et al. 1991
    n = len(scar); return scar.mean() * np.sqrt(n) / scar.std(ddof=1)

def kp_adjust(t, resid_matrix):    # Kolari & Pynnönen 2010; columns = events, aligned calendar days
    r = resid_matrix.corr().values; n = r.shape[0]
    rbar = (r.sum() - n) / (n * (n - 1))
    return t * np.sqrt((1 - rbar) / (1 + (n - 1) * rbar))

def gen_sign(cars, p_hat):         # Cowan 1992, H1: more negatives than expected
    n = len(cars); w = (cars < 0).sum()
    return (w - n * p_hat) / np.sqrt(n * p_hat * (1 - p_hat))

# Wilcoxon: stats.wilcoxon(scar, alternative="less")
# Firm-clustered mean: smf.ols("scar ~ 1", d).fit(cov_type="cluster", cov_kwds={"groups": d.ticker})
```

Note for `kp_adjust`: the residuals of different events sit on different calendar dates. Compute r̄ only over pairs whose estimation windows overlap in calendar time, or use the event-time alignment described in Kolari & Pynnönen (2010) [VERIFY implementation against the paper].

**4.3 Harm agreement:**

```python
def kappa(a, b):
    a, b = list(a), list(b); n = len(a); cats = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c)/n) * (b.count(c)/n) for c in cats)
    return (po - pe) / (1 - pe), po
def pabak(po, q): return (q * po - 1) / (q - 1)   # q = number of categories
```

**4.4 CUSUM and early-warning scoring:**

```python
def cusum(z, k=0.5, h=5.0):
    s, out = 0.0, []
    for v in z.fillna(0).values:
        s = max(0.0, s + v - k)
        if s > h: out.append(1); s = 0.0
        else: out.append(0)
    return pd.Series(out, index=z.index)

def score(alarms, events, W=10, L=2):
    """alarms: dict firm -> 0/1 Series on trading days; events: DataFrame(firm, T)."""
    leads, fa_eps, firm_years = [], 0, 0.0
    for f, a in alarms.items():
        idx = a.index; ev = events[events.firm == f]
        covered = np.zeros(len(a), bool)
        for T in ev.T:
            p = idx.searchsorted(T); lo, hi = max(0, p - W), min(len(a) - 1, p + L)
            covered[lo:hi + 1] = True
            hits = np.flatnonzero(a.values[lo:hi + 1]) + lo
            leads.append(p - hits[0] if len(hits) else np.nan)
        on = a.values.astype(bool) & ~covered
        fa_eps += int(on[0]) + int(((on[1:]) & (~on[:-1])).sum())   # episodes
        firm_years += len(a) / 252
    leads = np.array(leads)
    return {"early_recall": np.mean(leads >= 1), "fa_per_firm_year": fa_eps / firm_years,
            "median_lead": np.nanmedian(leads[leads >= 1]) if (leads >= 1).any() else np.nan}
```

**4.5 Threshold selection under the budget:** grid over h; pick the smallest h whose validation-year `fa_per_firm_year ≤ 1`.

## Phase 5 — "Training" and experimentation

There is no model training in the deep-learning sense. "Training" means:
- Estimating α and β per event (OLS on the estimation window).
- Fitting lexicons, thresholds and Kalman parameters on past years only.
- Optionally an L2-logistic model (`sklearn` or `statsmodels`) on the training years, with C chosen on the validation year.

Hyperparameters to tune on validation only: CUSUM k ∈ {0.25, 0.5, 1.0} and h (budget-driven), and the percentile p.

Fixed by pre-registration: W, L, B, h_horizon = 5.

**Reproducibility:**
- Seeds for the placebo (e.g., 2026) and the bootstrap.
- One config file (`config.yaml`) holding all windows.
- Every script reads it.

## Phase 6 — Evaluation

| Metric | Formula / tool | Interpretation |
|---|---|---|
| CAAR (%) | mean CAR × 100 | Economic size |
| SCAAR | mean SCAR | Size in volatility units, comparable to P4's −0.29 |
| BMP / KP t | §4.2 | Significance under event-induced variance / clustering |
| Share negative CARs | w/N + generalized sign Z | Breadth of the effect |
| Abnormal news volume | past-z of counts at τ | Media reaction (RQ3) |
| Early recall @ B = 1 | `score()` | Main RQ4 metric |
| FA per firm-year | `score()` | Must be ≤ 1 on *test* years |
| Median lead time | `score()` | How early |
| PR-AUC (h = 5) | `sklearn.metrics.average_precision_score` | Ranking quality on rare positives; report the base rate |
| Brier score | mean (p − y)² | Calibration of the optional logistic model |

**Comparison rule:** the proposed detector "wins" only if its ER beats B0, B1 and B2 at equal budget, with a firm-block bootstrap 95% CI of the difference excluding 0 [GUIDE Part 12].

## Phase 7 — "Application / prototype"

**Honest scoping:** the Guide's deliverable is evidence, not software. The "prototype" is:
1. A single command (`make all` or `run_all.py`) that regenerates every table and figure from frozen inputs.
2. A released replication package: linkage table, harm codes, lexicons, queries, code.
3. Optionally, a static results page: CAAR path, ER-vs-FA curve, per-harm coefficients.

**Do not** build a live monitoring dashboard: it would imply an operational early-warning capability the study hasn't shown.

## Phase 8 — Testing, validation, finalisation

**Tests to add (none exist today [VERIFIED]):**
- `test_event_returns`: synthetic stock with known α, β and a shock → recovered within tolerance.
- `test_no_lookahead`: perturb data after day t → features at t unchanged.
- `test_cusum`: a step change of +1σ starting at day 100 → alarm within the expected delay; no alarms on pure noise above the expected rate.
- `test_trading_day_alignment`: a Saturday event maps to Monday; 16:30 ET maps to the next day.
- `test_filters_regression`: re-running `step4_filters.py` on frozen inputs gives N = 244.

**Validation:** placebo SCAR distribution centred on 0; manual audit of 20 random events (date, firm, price move).

**Finalisation:** tag the release (`v1.0-analysis`), archive on OSF/Zenodo, and record deviations from the pre-registration.

---

# PART 7 — EXECUTION STATUS AUDIT

Audit date: 29 Oct 2026. Evidence = files in the repo, re-counted today. "κ recomputed" means computed in memory from repo CSVs without changing any file.

## 7.1 Progress table

| Component | Planned functionality | Work completed | Evidence | Status | Remaining work |
|---|---|---|---|---|---|
| Literature reading | Read and critique 6 full-text papers; gap analysis | Done in the Guide | `~/Downloads/Research_Guide_and_Proposal.pdf` (45 pp.) | **Verified Complete** | — |
| Systematic literature search | Confirm novelty; read the five-firm study and Sinanaj in full | None found | No search log in repo | **Planned** | Search Scopus/Google Scholar/SSRN; log queries |
| AIID snapshot | Frozen export | 1,689 incidents, 7,791 reports | `data/AIID_Excel_Export-20260921.xlsx` | **Verified Complete** | Record licence and hash |
| Report-date retrieval | Earliest report per incident | GraphQL + cache | `step3_screening.py`, `build/report_dates_cache.json` | **Verified Complete** | — |
| SEC EDGAR | Ticker list, submissions, facts | Downloaded locally | `data/SEC EDGAR/` (gitignored) | **Verified Complete** | Record download date |
| Listed-firm matching | Entity → listed parent | Alias map + exact match + block list | `step2_listed.py`, `build/listed_company_incidents.csv` (71 tickers) | **Verified Complete** | — |
| Recall pass | Firms named only in titles | 127 candidates → 10 vetted | `step3b_recall.py`, `build/recall_candidates.csv` | **Verified Complete** | — |
| Screening sheet | One row per incident × ticker, date flags, pilot | 510 rows / 460 incidents; 95 date flags | `build/screening_sheet.csv/.xlsx` | **Verified Complete** | — |
| Coding manual | Frozen rules | v1 → v2 → v3 (frozen 25 Sep 2026) | `coding_manual_v1..v3.md` | **Verified Complete** | — |
| Pilot rounds | κ before full coding | 3 rounds, κ 0.21 / 0.27 / −0.14 | Manual Appendix B; `pilot2_*`, `pilot3_*` | **Verified Complete** | Report all three in the paper |
| AI main coding | Code all non-pilot rows | 410 rows | `astra_out_*.csv`, `astra_all.csv` | **Verified Complete** | **Record model name/version/date** (manual §19) |
| Human validation | ≥ 50 blind rows; κ, PABAK | 30 of 50 coded. Type κ −0.04 (83%, PABAK 0.75); ticker κ 1.0; keep κ 0.27 | `validation_input.csv` (50), `validation_coderB_human.csv` (30), recomputed | **Partially Implemented** | Code the other 20; report κ + PABAK + CI; discuss the paradox |
| Adjudication | Resolve disagreements, UNCERTAIN, dates | 5 type disagreements, 26 UNCERTAIN, 75 dates | `adjudication_log.csv`, `uncertain_proposals.csv`, `date_proposals.csv` | **Verified Complete** | — |
| Final labels | `screening_final.csv` | keep = Y 399 | `build/screening_final.csv` | **Verified Complete** | — |
| Price data (stocks) | Daily adjusted closes | 72 tickers, 2000–2026-09-24 | `build/prices_panel.pkl` | **Verified Complete** | Hash, download date |
| Market index | Benchmark for the market model | Only in a 3-ticker test file | Not in `prices_panel.pkl` | **Partially Implemented** | Add `^SP500TR`/SPY |
| Earnings dates | Blackout ±5 td | 8-K 2.02 (235 events); yfinance (9) | `step4_filters.py`, `earn_source` | **Verified Complete** | Robustness excluding the 9 |
| Event filters | Pre/post, merge, earnings | N = 244 (240 high-conf), 47 firms | `build/final_sample*.csv`, `drop_log.csv` | **Verified Complete** | Set POST = 10; document merge order |
| Harm codebook | Frozen 6-category codebook | Written, frozen | `harm_codebook_v1.md` | **Verified Complete** | — |
| Harm coding | AI codes 237 + human 25 blind | Inputs drawn (5 batches, check seed 21) | `harm_input.csv`, `harm_batch_*`, `harm_check_input.csv` | **Planned** | Run, compute κ, adjudicate |
| Pre-registration | OSF registration | None | Not in repo | **Planned** | Write and register before returns |
| Controls / matched firms | Size, sector, controls | None | — | **Planned** | Phase 2 tasks 2.4–2.5 |
| News panel | Firm-day counts and tone | None; source not chosen | — | **Planned (decision needed)** | Choose source; build panel |
| Event study code | AR/CAR/tests/placebo | None | No script | **Planned** | Phase 4 |
| Early-warning code | Detectors + evaluation | None | No script | **Planned** | Phase 4 |
| Robustness | Grid of alternatives | None | — | **Planned** | Phase 6 |
| Alternative incident DB | OECD AIM / AIAAIC | None | — | **Planned** | Nice-to-have |
| Automated tests | Unit and regression tests | None | No `tests/` | **Planned** | Phase 8 |
| Paper draft | Full manuscript | Abstract and methodology drafts exist in the Guide only | Guide Parts 20–21 | **Planned** | Write |
| Statistical libraries | statsmodels, scipy | Not installed | `.venv/lib/.../site-packages` | **Planned** | `pip install` |

**Blocked items:** nothing is hard-blocked. The news source and WRDS/CRSP access depend on **decisions** about access you haven't confirmed, which the Guide lists as "First 5 implementation steps" #2.

## 7.2 How the completed components work and were verified

- **Matching (S2):** deterministic rules. Verified by the `correct_ticker` field: 19 of 510 rows set to N by coders, and 100% AI-human agreement on the validation sample.
- **Screening (S3):** verified by three pilot rounds, a validation sample, and logged adjudication. Weakness: κ on type.
- **Dates:** 95 flagged rows reviewed; 75 corrected; 7 corrections are low-confidence. The 4 low-confidence events that survived filtering are excluded in `final_sample_highconf.csv`.
- **Filters (S5):** verified by `drop_log.csv`. Today's recount reproduces 399 − 155 = 244.

## 7.3 What has NOT been executed

- No returns, abnormal returns, CARs or tests.
- No harm codes.
- No news data.
- No detectors.
- No placebo.
- No robustness checks.
- No figures.
- No paper text beyond the Guide's proposal drafts.

**There are no research results yet.**

---

# PART 8 — FINDINGS

## A. Verified findings (process and descriptive, not research results)

1. **Feasibility:** of 1,689 AIID incidents, 460 involve ≥ 1 U.S.-listed firm by our matcher (510 incident-firm pairs). 399 pairs pass coding (own-AI, correct firm, non-duplicate), and 244 survive the event-study filters. That is well above the ≥ 100 go/no-go gate and above the Guide's ~190 planning estimate.
2. **Concentration:** 5 firms (GOOGL, META, AMZN, TSLA, MSFT) account for 71% of events. This is itself a finding about which firms are publicly associated with AI incidents (and about reporting bias).
3. **Responsibility mix:** among screened pairs, 81% Type 1, 14% Type 3 (multi-firm studies) and 5% Type 2 (outside misuse). About a fifth of naive incident-firm links would be wrong attributions for an event study.
4. **Date quality:** 18.6% of AIID earliest-report dates needed review (social posts, preprints, blogs, or reports predating the incident). This matters for any event study using AIID dates.
5. **Earnings contamination:** 54 of 399 candidate events (14%) fall within ±5 trading days of an earnings release.
6. **Coding reliability:** human-AI agreement is high in raw terms (83% type, 100% ticker) but Cohen's κ is near zero for type because of extreme prevalence. Reliability claims must use PABAK/AC1 alongside κ.

## B. Expected findings (reasoned from prior work, not observed)

- **RQ1:** a small negative mean SCAR[−1,+1] is plausible. P4 found −0.29 SCAAR for ESG chatter spikes, and breach studies find negative reactions. But our events are concentrated in mega-cap firms with huge news flow, where a single incident is a small piece of information, so the effect could be close to zero.
- **RQ2:** SAFE (crashes, injuries) and PRIV may show larger reactions than DECEPT or ACCT, by analogy to P4's Social/Governance vs Environment split. This is exploratory and subgroups will be small (likely 20–70 events each).
- **RQ3:** a clear abnormal news-volume spike at T is very likely. Partly this is by construction (AIID collects reported incidents).
- **RQ4:** early recall at B = 1 may be low. Many incidents surface in one story, and P4's pre-event return effect suggests information may move first through channels a news detector can't see.
- **RQ5:** some pre-event drift may appear, either from leakage or from dating error. The early-alarm audit separates these.

## C. Hypotheses requiring experiments

| Hypothesis | Experiment | Evidence needed |
|---|---|---|
| H1: mean SCAR[−1,+1] < 0 | Exp 1 | BMP/KP t < −1.645 (one-sided 5%), firm-clustered CI below 0, outside the placebo distribution |
| Harm types differ | Exp 4 | BH-adjusted q < 0.05 on any harm contrast |
| Attention scales with CAR | Exp 3 | Negative slope of CAR on abnormal volume, firm-clustered |
| Topic CUSUM ER > baselines | Exp 2 | Bootstrap CI of ER difference excludes 0 at B = 1 |
| Pre-event drift exists | Exp 3 | SCAR[−5,−2] or [−21,−2] < 0 significantly |

## D. Possible negative or unexpected findings, and what they would mean

| Outcome | Meaning | Still publishable? |
|---|---|---|
| SCAR ≈ 0 with a tight CI | Markets don't price AI incidents in the short term at large caps (yet) | Yes, as a well-powered null. Compare with P4 and breaches |
| Effect vanishes without GOOGL/META | Result driven by two firms | Report as fragile; firm-level heterogeneity becomes the story |
| Effect only post-2022 | Investor attention to AI risk rose after ChatGPT | Interesting period result (exploratory) |
| Topic CUSUM = generic baseline | AI-specific content adds nothing over attention | Yes: "external AI monitoring adds nothing beyond watching news volume" |
| Most early alarms are date errors | AIID dates lag the first public mention | Methodological contribution: AIID date-quality warning |
| Positive CARs | Unlikely. Check data errors, then consider "AI news = attention to AI leadership" | Report with caution |

## E. Result-table templates (to fill)

**Table 1 — Event-study results (RQ1).**

| Window | N | CAAR (%) | SCAAR | t_BMP | t_KP | Clustered p | % negative | Gen. sign Z | Wilcoxon p | Placebo p |
|---|---|---|---|---|---|---|---|---|---|---|
| [−1,+1] | | | | | | | | | | |
| [0,+1] | | | | | | | | | | |
| [0,+5] | | | | | | | | | | |
| [−5,−2] | | | | | | | | | | |
| [−21,−2] | | | | | | | | | | |

**Table 2 — Harm types (RQ2).** Columns: harm code, N, mean CAR[−1,+1], γ̂, clustered SE, p, BH q.

**Table 3 — Early warning (RQ4), test years pooled.** Columns: detector, ER @ B = 1 (Wilson CI), FA/firm-year (test), median lead, PR-AUC (h = 5) with base rate, ΔER vs proposed (bootstrap CI).

**Figures:**
1. Attrition funnel.
2. CAAR path τ = −21…+10 with 95% CI.
3. Abnormal news volume path.
4. ER-vs-FA curve per detector.
5. Lead-time histogram.
6. Harm-type coefficient plot.
7. Placebo distribution with the real estimate marked.

---

# PART 9 — EXPERIMENTAL DESIGN AND EVALUATION STRATEGY

All experiments follow [GUIDE Part 15].

| # | RQ | Hypothesis | Input | Procedure | Metrics | Success criterion | Insight |
|---|---|---|---|---|---|---|---|
| 1 Baseline event study | RQ1 | SCAR[−1,+1] < 0 | Events + prices + market index | Market model [T−250,T−31]; windows; Placebos A and B | SCAAR, CAAR %, BMP, KP, clustered, sign, Wilcoxon | Significant negative and outside the placebo distribution | Do AI incidents carry a short-term market cost? |
| 2 Early warning | RQ4 | Topic CUSUM ER > B0, B1, B2 | Firm-day news panel + events + controls | Rolling origin (fit ≤ Y−2, threshold Y−1, test Y) | ER @ B = 1, FA/fy, median lead, PR-AUC | Bootstrap CI of ΔER excludes 0 vs every baseline | Can public signals anticipate disclosure? |
| 3 Timing | RQ3, RQ5 | Pre-event drift; attention ↔ CAR | All | SAAR and abnormal volume τ = −21…+10; regress CAR on attention | SAAR CIs; slope | Significant pre-event SCAR / slope | When do reactions occur? |
| 4 Harm types | RQ2 | Harm types differ | Events + harm codes + controls | OLS with firm-clustered SEs, sector and year FE | γ̂, q (BH) | q < 0.05 (exploratory) | Which harms matter? |
| 5 Ablation | RQ4 | Each component helps | As Exp 2 | Remove one component at a time at a fixed budget | ΔER, Δlead (bootstrap) | CI of drop excludes 0 | What drives warning? |
| 6 Robustness | All | Conclusions stable | All | See list below | Same as main | No sign flip / significance loss | Fragility |
| 7 Placebo / randomisation | RQ1, RQ4 | Not chance | All | 1,000 re-datings within firm-year; control-firm assignment | Empirical p | p < 0.05 | Chance benchmark |

**Robustness list (Exp 6):**
- Estimation windows [−122,−2] and 90 days.
- T ± 1 trading day.
- Market-adjusted returns.
- Fama–French 3-factor (needs Ken French data library factors [VERIFY]).
- Exclude the top-5 firms; exclude GOOGL+META only.
- Exclude events with legal, merger, guidance, recall or CEO news.
- Pre/post 30 Nov 2022.
- High-confidence dates only (240) vs all (244).
- 2016+ vs full sample.
- Exclude the 9 yfinance-earnings events.
- Exclude ADRs (BABA, BIDU, XPEV, …).
- Exclude `subsid`-matched events (37).
- Exclude recall-sourced events (5).
- Alternative incident DB.
- W ∈ {5, 21}; B ∈ {0.5, 2}.
- Winsorised returns.

**Ablations (Exp 5):** topic vs generic signal; CUSUM vs single-day threshold; volume-only vs volume + tone; tone-only; per-harm lexicons vs a pooled lexicon; 250-day vs 60-day baseline vs raw counts; logistic with vs without prior-incident count.

**Hyperparameters:** chosen on validation years only (CUSUM k, h, percentile p, logistic C). Pre-registered constants: W = 10, L = 2, B = 1, h = 5, windows.

**Error analysis:**
- For RQ1: inspect the 10 most negative and 10 most positive CARs. Look for confounding news (read the headlines on T) and date errors.
- For RQ4: audit every early alarm and a random 50 false alarms. Classify whether each "false alarm" is an unrecorded incident.

**Avoiding leakage, cherry-picking and unsupported conclusions:**
1. Pre-register before merging returns.
2. Freeze the harm codes before computing returns (already part of the codebook procedure).
3. Use past-only rolling statistics (`shift(1)`).
4. Fit lexicons on training years.
5. Never use harm type or AIID taxonomies as RQ4 features.
6. Estimation window ends at T−31, before any pre-event window.
7. Report every pre-registered window, not just significant ones.
8. Apply BH correction for families of tests.
9. Use association language throughout.

**Reproducibility:**
- Fixed seeds, frozen snapshot, cached prices with hashes.
- One config file and one entry-point script.
- Release the linkage table and code.

**Power note:** the Guide's ~190-event estimate for 80% power assumes P4-like effect size and independent events. With 71% of events at 5 firms the *effective* N is lower. Compute a design-effect-adjusted power or simulate it: resample CARs under a planted effect with firm clustering. Treat the result as a planning estimate.

---

# PART 10 — LIMITATIONS, CHALLENGES, IMPROVEMENTS

**Known limitations (observed in the data or code):**

| # | Limitation | Cause | Impact | Detection | Mitigation | Residual trade-off |
|---|---|---|---|---|---|---|
| K1 | Type-κ ≈ 0 on validation; 30 of 50 rows coded | Extreme Type-1 prevalence; small n | Reviewers may question coding reliability | Recomputed κ, PABAK | Code 20 more; report κ, PABAK, Gwet's AC1 and a bootstrap CI; explain the paradox; show the main result is robust to dropping rows where coders disagreed | κ will remain low however good agreement is |
| K2 | Event concentration (top 5 = 71%) | AIID coverage of big tech | Low effective N; results driven by a few firms | Ticker counts | Clustered tests; leave-top-firms-out; firm fixed effects in RQ2 | Less power |
| K3 | Missing market index | Not downloaded into the panel | Event study can't run | Panel columns | Add `^SP500TR`/SPY | — |
| K4 | Yahoo ≠ CRSP | Access | No delisting returns; revisions | — | Document; CRSP robustness if WRDS is available | Minor for large caps |
| K5 | Dates are day-level only (no time stamp) | AIID report dates | The 16:00 ET rule can't be applied to T | — | [−1,+1] primary window; ±1-day robustness | Slightly diluted effect |
| K6 | AI coder model not recorded | Process gap | Reproducibility | Repo search | Add to `DATA_MANIFEST.md` now (from chat logs or billing records) | If unknown, state "unrecorded" |
| K7 | Adjudicator = rule designer, and all disagreements went to the AI's answer | Single-author project | Perceived bias | Adjudication log | Publish the log; sensitivity analysis excluding adjudicated rows | — |
| K8 | Reporting bias | AIID collects media-covered incidents | Results generalise only to *reported* incidents | — | Scope statement; size controls | — |
| K9 | 9 events lack SEC earnings dates | Foreign issuers | Possible contamination | `earn_source` | Robustness excluding them | — |
| K10 | Pre-2016 events (13) | Filter not applied | News panel won't cover them | Year counts | 2016+ primary | Fewer events |

**Risks not yet observed:**

| Risk | Cause | Detection | Mitigation |
|---|---|---|---|
| News firm-name noise | GDELT machine extraction | Hand-check 200 articles | Exclusion lists; fall back to a library database |
| Too few test-year events for RQ4 | Events spread over 10 years | Count events per test year | Pool test years; report CIs; treat RQ4 as secondary |
| Lexicon leakage | Fitting on all years | Code review; `test_no_lookahead` | Training-year-only fitting |
| LLM leakage | Using a modern LLM to score old news | — | Don't. Use lexicons/VADER |
| Mis-dated events create fake early warnings | AIID dates later than first coverage | Early-alarm audit | Report both with and without date-corrected events |
| Cross-sectional dependence | Same-day events across firms | KP r̄ | KP adjustment |
| Multiple testing | Many windows and subgroups | — | Pre-registration; BH |
| Compute or quotas | BigQuery free tier | Monitor query bytes | Partition by date; select columns |

**Interpretability:** all methods are transparent (OLS, CUSUM, lexicons). No black-box models.

**Bias and fairness of the study itself:** naming firms in connection with incidents carries reputational implications. Use association language and state that results are not investment advice [GUIDE §3.12].

---

# PART 11 — DETAILED PLAN OF ACTION

Effort figures are **estimates** for one person working part-time on this project.

## 11.1 Critical path

```
A1 market index ─┐
A2 POST=10 ──────┤
A4 validation +20 ──► A5 harm coding ─► A6 pre-registration ─► B1 event study ─► B2 placebo ─► B4 robustness ─┐
                                                                                                               ├─► D paper
C1 choose news source ─► C2 news panel ─► C3 topic lexicon ─► C4 detectors ─► C5 rolling eval ─► C6 ablation ─┘
A3 literature search (parallel, must finish before writing the intro)
```

**Parallel tracks:** Track A/B (event study) and Track C (news and early warning) can run side by side once A6 is done. Track C1–C3 can start before A6, as long as no returns are touched.

## 11.2 Tasks

### Phase A — Close out data preparation (immediate)

| ID | Task | Why | How | Input | Deliverable | Verify | Priority | Effort (est.) |
|---|---|---|---|---|---|---|---|---|
| A1 | Add the market index | Market model needs it | Phase 2 Task 2.1 script | Yahoo | Updated `prices_panel.pkl` | ≥ 99% coverage since 2005 | P0 | 1 h |
| A2 | Set POST = 10; re-run filters | Consistency with τ = +10 | Edit config; run `step4_filters.py` | Repo | Same N = 244 | `drop_log.csv` unchanged | P0 | 0.5 h |
| A3 | Systematic literature search | Novelty claim | Queries: "AI incident" AND (event study OR abnormal return OR stock); "algorithmic bias" AND "stock market"; AIID citations. Read the five-firm study and Sinanaj in full | Scholar, SSRN, Scopus | `docs/lit_search_log.md` | Query log, inclusion table | P0 | 2–3 days |
| A4 | Complete the human validation (20 rows) | Manual §19 requires ≥ 50 | Code the remaining rows of `validation_input.csv` blind | Manual v3 | 50-row κ / PABAK / AC1 | Re-run κ (in a copy, not overwriting `disagreements.csv`) | P0 | 0.5 day |
| A5 | Harm coding | RQ2; must precede returns | AI codes 5 batches; you code 25 blind; κ; adjudicate | Codebook v1 | `harm_codes.csv`, `harm_adjudication_log.csv` | All 237 incidents coded; κ reported | P0 | 1–2 days |
| A6 | Pre-register on OSF | Prevents garden-of-forking-paths | Template: hypotheses, sample, windows, tests, detectors, exclusions | This report, Part 9 | OSF link + PDF in repo | Timestamp before A1's returns are computed | P0 | 1 day |
| A7 | Record provenance | Reproducibility | `DATA_MANIFEST.md`: snapshot date, AI model, hashes | — | File | Present | P1 | 1 h |
| A8 | Install stats libraries; `requirements.txt` | Analysis | `pip install` | — | File | Imports work | P0 | 0.5 h |

### Phase B — Event study (after A6)

| ID | Task | Deliverable | Verify | Priority | Effort (est.) |
|---|---|---|---|---|---|
| B0 | Unit test on synthetic data | `tests/test_event_returns.py` | Recovers β and the shock | P0 | 0.5 day |
| B1 | AR/CAR for 244 events; RQ1 tests | `event_car.csv`, Table 1 | Spot-check 5 events by hand in a spreadsheet | P0 | 2 days |
| B2 | Placebos A and B (1,000×) | Placebo distribution plot | Centred near 0 | P0 | 1 day |
| B3 | Controls and matched firms | `controls.csv`, control prices | Each event has ≥ 1 control | P1 | 1–2 days |
| B4 | Robustness grid | Robustness table | All rows filled | P1 | 2 days |
| B5 | RQ2 harm regression | Table 2, coefficient plot | Clustered SEs, BH q | P1 | 1 day |
| B6 | RQ5 pre-event and CAAR path | Figure 2 | CIs plotted | P1 | 0.5 day |

### Phase C — News and early warning (C1–C3 can start now)

| ID | Task | Deliverable | Verify | Priority | Effort (est.) |
|---|---|---|---|---|---|
| C1 | Confirm access: WRDS/CRSP, library news, GDELT BigQuery | Decision note | Written | P0 | 1 day |
| C2 | Build the firm-day news panel (event firms + controls) | `news_panel.parquet` | 200-article precision check ≥ 90% | P0 | 4–7 days |
| C3 | Lexicons from training years | `lexicons/*.txt` | Built only from ≤ Y−2 | P1 | 1–2 days |
| C4 | Baselines B0–B2 and topic CUSUM | `step9_warning.py` | `test_cusum`, `test_no_lookahead` | P0 | 2–3 days |
| C5 | Rolling-origin evaluation; bootstrap | Table 3, ER-FA curve | FA ≤ 1 on validation years | P0 | 2 days |
| C6 | Ablations; early-alarm audit | Ablation table; audit CSV | Every early alarm classified | P1 | 2–3 days |
| C7 | RQ3 attention event study | Figure 3 | Spike at T | P1 | 1 day |

### Phase D — Write and defend

| ID | Task | Deliverable | Priority | Effort (est.) |
|---|---|---|---|---|
| D1 | Methods section (adapt Guide Part 21 to what was actually done, including deviations) | Draft | P0 | 2 days |
| D2 | Results and discussion | Draft | P0 | 3–4 days |
| D3 | Intro and related work (after A3) | Draft | P0 | 2–3 days |
| D4 | Replication package and release tag | Repo + OSF/Zenodo | P1 | 1 day |
| D5 | Slides and defence prep (Part 12) | Deck | P1 | 1–2 days |

## 11.3 Immediate next actions (this week)

1. A1 + A2 + A8 (about half a day total).
2. A4: code the last 20 validation rows.
3. A5: run harm coding.
4. A6: draft the pre-registration.
5. C1: check WRDS and library news access, and try a GDELT BigQuery query for one firm.

## 11.4 Milestones

| Milestone | Definition of done |
|---|---|
| M1 Data frozen | A1–A8 complete; pre-registration timestamped |
| M2 RQ1 answered | Table 1 + placebo + core robustness |
| M3 News panel ready | Panel built and precision-checked |
| M4 RQ4 answered | Table 3 + ER-FA curve + audit |
| M5 Draft paper | All sections written |
| M6 Submission / defence | Replication package released |

## 11.5 Checklist

- [ ] Market index in the price panel
- [ ] POST = 10, N re-confirmed
- [ ] `requirements.txt`, `DATA_MANIFEST.md` (including AI coder model)
- [ ] Validation 50/50 rows; κ + PABAK + AC1 + CI
- [ ] Harm codes for 237 incidents; κ on 25+; adjudication log
- [ ] Literature search log; five-firm study read
- [ ] OSF pre-registration
- [ ] Event-study unit test passes
- [ ] Table 1, placebo, CAAR figure
- [ ] Controls and matched firms
- [ ] Robustness table
- [ ] Harm regression
- [ ] News source chosen; panel built; precision ≥ 90%
- [ ] Detectors + rolling evaluation + bootstrap
- [ ] Ablation + early-alarm audit
- [ ] Paper sections; deviations from pre-registration listed
- [ ] Release tag + archive

---

# PART 12 — FINAL REPORT AND PRESENTATION PREPARATION

## 12.1 Paper structure

| Section | Content | Tables/figures |
|---|---|---|
| Abstract | Part 1.1, updated with results | — |
| 1 Introduction | Problem, the original internal-monitoring idea and why it is untestable, the modified RQs, contributions | — |
| 2 Related work | Streams A (in-model monitoring: P1, P5, P6), B (reputation and markets: P2, P3, P4, Sinanaj), C (AI incident databases) | Literature comparison table (Part 3.2) |
| 3 Hypotheses | H1 (RQ1), RQ2–RQ5, H1 (RQ4) | — |
| 4 Data | AIID, matching, coding manual, reliability, dates, filters, prices, earnings, news, controls | **Attrition funnel**; κ/PABAK table (pilots + validation); event counts by year, firm and harm type |
| 5 Methodology | Market model, tests, placebos, regression; news features; detectors; rolling origin; early-warning definitions | Early-warning definitions table; timeline diagram (estimation window → pre-event → event window) |
| 6 Results | RQ1, RQ5, RQ3, RQ2, RQ4 | Tables 1–3; CAAR path; news path; ER-FA curve; lead-time histogram; harm coefficient plot; placebo plot |
| 7 Robustness | Grid | Robustness table |
| 8 Discussion | Meaning, comparison with P4 and breach studies, what external monitoring can and cannot do, the internal-monitoring agenda | — |
| 9 Limitations | Part 10 | — |
| 10 Conclusion and future work | Internal-monitoring partner study; HMDA fairness-drift benchmark (Option D); alternative databases | — |
| Appendices | Coding manual v3, harm codebook, prompts, alias map, pre-registration, deviations | — |

## 12.2 Presentation outline (12–15 slides)

1. Title and one-sentence idea.
2. Why it matters: AI failures, regulation, reputational stakes.
3. The original idea and why it can't be tested (the dashboard analogy).
4. What the literature shows and doesn't (three streams, gap).
5. RQs and hypotheses.
6. Data pipeline and attrition funnel (1,689 → 510 → 399 → 244).
7. Coding rigour: manual v3, pilots, validation, honest κ discussion.
8. Event-study method (timeline graphic).
9. Early-warning definition (smoke-detector budget).
10. Results: RQ1 (once available).
11. Results: RQ2–RQ5.
12. Robustness and placebo.
13. Limitations.
14. Contributions and future work.

## 12.3 Likely questions and grounded answers

1. **Where is the novelty?** No large-sample, harm-type-stratified, confound-controlled AI-incident event study with a leakage-controlled early-warning test was found in the supplied literature. The novelty is an application and protocol, confirmed by the systematic search (task A3), and I distinguish the five-firm 2024 study explicitly.
2. **Why is your κ negative?** Both coders labelled ~90% of rows Type 1, so chance agreement (0.84) slightly exceeds observed agreement (0.83). This is the known kappa paradox. PABAK is 0.75, and ticker agreement is 100%. I also show results are robust to excluding rows where the coders disagreed.
3. **Why an AI coder?** Scale and consistency under a frozen manual and fixed prompt, with a blind human validation sample and logged adjudication. I report the model and version.
4. **Why do returns measure reputation?** They don't purely. They reflect expected costs plus reputation. I call them "market reaction" and pair them with media attention.
5. **How do you know the date is right?** T = earliest linked report, with 95 flagged dates human-reviewed and 75 corrected. The [−1,+1] window and ±1-day robustness handle residual error. The high-confidence subsample is the primary sample.
6. **Isn't this dominated by Google and Meta?** Yes, 45% of events. I use firm-clustered inference, KP adjustment, and leave-top-firms-out tests, and I report heterogeneity.
7. **How do you avoid look-ahead?** Estimation window ends at T−31; all rolling statistics are past-only; lexicons and thresholds come from earlier years; harm types are never features; pre-registration.
8. **Why CUSUM?** It accumulates small persistent increases that single-day spike rules miss. It is transparent, needs no labels to run, and has well-understood behaviour.
9. **Why not deep learning?** A few hundred events; interpretability and leakage control matter more than capacity; LLMs trained after the period could already "know" the incidents.
10. **What if nothing is significant?** A well-powered null with tight CIs is informative: AI incidents may not be priced in the short term at large caps, and public news may not anticipate them. Either way it shows the limits of external monitoring.
11. **Why earnings exclusion ±5 days?** It follows P4. Earnings dominate returns, and 14% of candidates were affected.
12. **Why not Twitter/X?** Academic API access ended in 2023 and bots distort volume [GUIDE]. News is the primary signal.
13. **How does this connect to your internal-monitoring idea?** It measures the downstream consequences and the limits of external warning, which defines what an internal-monitoring study with partner data would need to beat.
14. **Why Yahoo, not CRSP?** Access. Adjusted closes are adequate for large-cap daily event studies. CRSP is a robustness check if WRDS is available.
15. **What is one row of your data?** Main analysis: one AI incident at one listed firm. Early warning: one firm on one trading day.

## 12.4 What to tell your supervisor now (status statement)

> "The sample is built and validated: 244 incident–firm events at 47 listed firms from the AI Incident Database, after a three-round coding manual, an AI-coded main pass with human validation and logged adjudication, date verification, and filters for price history, overlapping events and earnings. Harm-type coding is set up under a frozen codebook. Next, I will finish the validation sample, code harm types, pre-register, then run the event study. In parallel I will build the news panel for the early-warning test. No returns have been computed yet, by design."

---

## References (verify page numbers before citing)

- Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study methodology under conditions of event-induced variance. *Journal of Financial Economics*, 30(2), 253–272.
- Byrt, T., Bishop, J., & Carlin, J. B. (1993). Bias, prevalence and kappa. *Journal of Clinical Epidemiology*, 46(5), 423–429.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *JRSS Series B*, 57(1), 289–300.
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46.
- Cowan, A. R. (1992). Nonparametric event study tests. *Review of Quantitative Finance and Accounting*, 2, 343–358.
- Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. *Journal of Clinical Epidemiology*, 43(6), 543–549.
- Kolari, J. W., & Pynnönen, S. (2010). Event study testing with cross-sectional correlation of abnormal returns. *Review of Financial Studies*, 23(11), 3996–4025.
- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13–39.
- McGregor, S. (2021). Preventing repeated real world AI failures by cataloging incidents: The AI Incident Database. *Proceedings of AAAI*, 35(17), 15458–15463.
- Page, E. S. (1954). Continuous inspection schemes. *Biometrika*, 41(1/2), 100–115.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *JASA*, 22(158), 209–212.
- Papers P1–P6 and the Stream-C abstracts: full citations as listed in `Research_Guide_and_Proposal.pdf`, pages 3 and 23.
- [VERIFY] Five-firm AI-incident event study, *Finance Research Letters* (2024). Locate and cite exactly.
- [VERIFY] GDELT 2.0 GKG documentation and BigQuery table names: https://www.gdeltproject.org/data.html
