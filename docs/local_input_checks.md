# Offline input checks and next work

This additive patch does not change step4_filters.py, POST, sample membership or annotations.

Run from the repository root (use the project's existing Python environment):

```bash
python -m unittest discover -s tests -v
python scripts/check_local_inputs.py --output results/local-input-check-01.json
```

The checker needs only Python's standard library. It reads local files, hashes inputs,
checks ticker mappings and follows historical SEC filenames for keep=Y candidate firms.
It refuses to overwrite an existing report. Exit code 2 means input issues were found;
the JSON report is still saved. Exit code 0 means these limited structural checks passed,
not that earnings coverage, benchmark availability or the full pipeline is validated.

Send the issues and firms sections back for review; full data uploads are unnecessary.
The report contains relative filenames and hashes rather than local absolute paths.

## Tests executed here
18 tests passed: the existing 10 validation tests and 8 new checks. New checks cover
missing files/history, rejecting companyfacts, hashing a price file without unpickling,
and isolated execution of the legacy event_date/trading_index functions.
These are not end-to-end filter tests. No full dataset run has occurred here.

## Blind coding
The repo is public. Send the coder only the blank sheet, manual and coder note; ask them
not to inspect AI labels or results. Record any actual exposure before claiming independent
validation. Public availability alone does not establish that exposure occurred.
UNREADABLE rows are unresolved, not completed. Their coding fields must all be blank.
The agreement script skips blank fields; it does not itself enforce the UNREADABLE rule.
A completed-file validator must enforce that rule before combining the 30 and 20 files.

## Earnings coverage gaps — observed in the local dataset; not yet corrected

Found on 29 October 2026 by comparing `results/local-input-check-01.json` (exit 0, no
structural issues) with `build/final_sample_all.csv`. The checker's exit code 0 confirms
only that referenced files exist and parse; it does not certify earnings coverage.
`step4_filters.py` currently treats any firm with SEC 8-K 2.02 dates as covered
(`earn_source = sec_8k_2.02`) without checking that those dates span the event's
±5 trading-day blackout window. Filters and sample membership are unchanged here.

**Gap A — events before the mapped CIK's filing history.** GOOGL maps to CIK 0001652044
(Alphabet Inc.), whose earliest filing in the local submissions data is 2015-10-02.
Earnings releases before then were filed by the predecessor registrant, Google Inc.
(predecessor CIK still to be verified and documented), which is not consulted. No blackout
dates existed for these events, yet they carry `earn_source = sec_8k_2.02`:

| incident_id | ticker | event_date |
|---|---|---|
| 45 | GOOGL | 2011-04-05 |
| 19 | GOOGL | 2013-02-05 |
| 18 | GOOGL | 2015-04-04 |
| 25 | GOOGL | 2015-06-26 |

**Gap B — blackout windows extending beyond the SEC snapshot.** The SEC download date is
unrecorded. The latest filing date across the 62 checked firms is 2026-07-13; this is an
**estimated** snapshot cutoff, not a verified download date, and a firm's last filing date
alone cannot certify coverage. For the events below, the +5 trading-day end of the
blackout window (computed on the ticker's price calendar) falls after 2026-07-13, so an
earnings release inside the window could be missing:

| incident_id | ticker | event_date | window end (+5 td) | firm's last local filing |
|---|---|---|---|---|
| 1584 | META | 2026-07-14 | 2026-07-21 | 2026-07-13 |
| 1602 | AMZN | 2026-07-17 | 2026-07-24 | 2026-07-09 |
| 1630 | CZR | 2026-07-29 | 2026-08-05 | 2026-07-08 |
| 1630 | MGM | 2026-07-29 | 2026-08-05 | 2026-07-02 |
| 1631 | ZTS | 2026-07-30 | 2026-08-06 | 2026-06-22 |
| 1649 | META | 2026-08-05 | 2026-08-12 | 2026-07-13 |
| 1682 | GOOGL | 2026-09-03 | 2026-09-11 | 2026-07-09 |

All 11 affected event–ticker pairs currently carry `earn_source = sec_8k_2.02`, which
overstates coverage. The planned treatment: verify Google Inc.'s predecessor CIK and dates
and include its filing history; establish a documented snapshot boundary, refreshing into a
separate snapshot or flagging coverage as unresolved; and record the date source separately
from whether the full ±5 trading-day window (including dates after the event) was covered.

## Next implementation gate
Review the local inventory before integrating new filter logic. Implement full tests for
history boundaries, weekend/holiday alignment, event merging, earnings coverage gaps and
empty samples. Document the proposed filing-date/announcement-date treatment. Then compare
old and revised filters on the same frozen inputs into separate output directories.
Do not assume N=244 must remain constant after fixing a genuine filtering defect. Explain
any changed event keys and exclusion reasons. Freeze decisions before outcome analysis.
