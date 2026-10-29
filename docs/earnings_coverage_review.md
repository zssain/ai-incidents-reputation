# Earnings coverage review

Started 29 October 2026 on branch `phase1-validation-fixes` (HEAD `db5fb2e`). Covers the 11
event–ticker pairs listed in `docs/local_input_checks.md` ("Earnings coverage gaps").
`step4_filters.py`, the sample (N = 244) and all annotations are unchanged.

## Step 1 — Frozen baseline (done)

`scripts/freeze_baseline.py --name baseline-20261029` created `snapshots/baseline-20261029/`:
- `build/`: byte-for-byte copy of all 15 files in `build/`, each verified by SHA-256 against
  the original, then made read-only.
- `manifest.json` (read-only): SHA-256 of every copied file, of the AIID export, and of the
  157 SEC files the earnings filter reads for the 62 keep=Y candidate firms
  (`company_tickers.json` + 156 base/historical submissions files).
- The full SEC trees are fingerprinted, not copied (originals stay in `data/`, untouched):

| Tree | Files | Size | Listing SHA-256 (prefix) |
|---|---|---|---|
| `submissions/` | 982,130 | 5.7 GB | `cdc5f415fde64afe` |
| `companyfacts/` | 20,052 | 19.0 GB | `1271f51d98e6d565` |

What the fingerprints contain:
- **157 SEC filter inputs:** full SHA-256 **content** hashes, file by file.
- **Full `submissions/` and `companyfacts/` trees:** **no content hashes.** The listing
  digest is a SHA-256 of the sorted (relative path, size in bytes, mtime in ns) tuples only.
  It detects added, removed or renamed files and changes in size or modification time. It
  cannot detect a content change that leaves size and mtime unchanged.

Fingerprints detect changes; they cannot restore the original files. The original SEC
folders in `data/SEC EDGAR/` are therefore preserved untouched and are not modified by any
step of this review. File mtimes are not download dates; the SEC download date remains
**unrecorded**. Any refreshed SEC data goes to a separate, dated directory.

## Step 2 — Google Inc. predecessor filings (done for Gap A)

Verified in the local submissions data: CIK **0001288776**, registrant name "GOOGLE INC.",
SIC 7370 (same as Alphabet, CIK 0001652044, tickers GOOGL/GOOG). All three historical files
it references are present locally. Its filings span 2001-03-12 to 2017-11-03, with 46
8-K item 2.02 filings from 2004-10-21 to 2015-10-22; Alphabet's 8-K 2.02 filings begin
2015-10-22. Earliest and latest filing dates do not prove uninterrupted coverage. The
predecessor records support checking the four early GOOGL events below; they are not a
certification of coverage for every date. The predecessor relationship (Alphabet became Google's holding company in the October 2015
reorganisation) is inferred from these records; cite an SEC filing (e.g., the
reorganisation 8-K) before relying on it in the paper.

Each event's ±5 trading-day window (GOOGL price calendar) was checked against Google Inc.'s
8-K 2.02 filing dates:

| Event–ticker | T | ±5 td window | Google Inc. 8-K 2.02 dates before and after window? | Nearest 8-K 2.02 (offset, td) | Original decision | Diagnostic decision | Evidence / reason |
|---|---|---|---|---|---|---|---|
| 45–GOOGL | 2011-04-05 | 2011-03-29 … 2011-04-12 | Yes | 2011-04-14 (+7) | Retained | **Retained in the diagnostic review; production filter unchanged** | No 8-K 2.02 filing date within ±5 td |
| 19–GOOGL | 2013-02-05 | 2013-01-29 … 2013-02-12 | Yes | 2013-01-22 (−10) | Retained | **Retained in the diagnostic review; production filter unchanged** | No 8-K 2.02 filing date within ±5 td |
| 18–GOOGL | 2015-04-04 | 2015-03-27 … 2015-04-13 | Yes | 2015-04-23 (+13) | Retained | **Retained in the diagnostic review; production filter unchanged** | No 8-K 2.02 filing date within ±5 td |
| 25–GOOGL | 2015-06-26 | 2015-06-19 … 2015-07-06 | Yes | 2015-07-16 (+13) | Retained | **Retained in the diagnostic review; production filter unchanged** | No 8-K 2.02 filing date within ±5 td |

These diagnostic decisions agree with the original ones, which before this review rested
on missing evidence. The evidence uses 8-K 2.02 **filing** dates as proxies for earnings
announcement dates. `step4_filters.py` still consults only Alphabet's CIK; the production
filter will change only after the full diagnostic comparison (step 5).

Caveats:
- 8-K 2.02 **filing** dates are a proxy for the announcement date. The nearest filing (+7 td
  for event 45) is outside the window even with a ±1-day filing lag.
- Event 45 has an earnings filing at τ = +7. That lies outside the ±5 blackout and the
  [0, +5] window, but inside the planned τ = −30…+10 path, so that event's extended path
  cannot be interpreted entirely as an AI-incident response.

## Return-window treatment (proposed; to settle before registration)

| Analysis | Treatment |
|---|---|
| Primary [−1, +1] result | Keep the ±5 trading-day earnings blackout |
| Extended −30…+10 path | Flag every event with an earnings date inside the path; report a sensitivity analysis excluding the flagged events |

The primary blackout is not widened because of event 45 alone; whichever rule is chosen
applies to all events consistently.

## Steps 3–5 — still to do

3. Acquire a separate, dated SEC snapshot for the seven Gap B pairs (META 1584, AMZN 1602,
   CZR 1630, MGM 1630, ZTS 1631, META 1649, GOOGL 1682); keep the original snapshot intact.
4. Revise coverage reporting: record the date source separately from whether the full ±5 td
   window is supported; unknown coverage stays explicitly unresolved. Add the Google Inc.
   CIK as a predecessor for GOOGL before 2015-10-22.
5. Re-run the filters into a separate output directory and compare with the baseline by
   event–ticker key and exclusion reason, without forcing N = 244.
