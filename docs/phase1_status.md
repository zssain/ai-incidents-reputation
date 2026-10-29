# Phase 1: validation and output protection

Implemented 29 October 2026 against commit 53b689c7762d8a7653ab783e496db6a19d3071d0.

## Changes and evidence
- Kappa returns undefined for empty/constant-label inputs and rejects unequal lengths.
- Coder inputs require valid fields, integer IDs, nonblank tickers, valid labels and unique keys.
- Alignment is one-to-one. Missing labels are excluded per field; unmatched keys are reported.
- Each run requires a new output directory containing metrics, confusion matrices and disagreements.
- Screening refuses existing master/coder outputs before third-party imports, input reads or network access.
- README points to frozen manual v3. No manual or original annotation edits.

Executed: `python -m unittest discover -s tests -v`: 10 tests passed.
Executed agreement CLI on committed validation CSVs: 30 matched rows; 20 unmatched AI keys;
responsibility kappa -0.0416667, agreement 0.8333333; ticker kappa 1, agreement 1;
keep kappa 0.2682927, agreement 0.8666667. Nine field-level disagreements across five rows.
Uniform-chance adjusted agreement is explicitly parameterized by category count; it does
not replace the manual's kappa criterion. Undefined kappa is saved blank.

## Local application notes (29 October 2026)
- Branch `phase1-validation-fixes` already existed at 53b689c (same as `master`, no extra
  commits), so the patch was applied on it instead of being created with `git switch -c`.
- The README hunk did not apply because the committed `README.md` has no trailing blank line.
  The other six files were applied with `git apply --exclude=README.md`. The README changes
  (manual v3 reference and the "Phase 1: safe validation" section) were then added by hand
  with identical text and placement.
- The project `.venv` has no `pip`, so `pip install -r requirements-validation.txt` was not
  run. Installed versions already satisfy the ranges: pandas 3.0.6, openpyxl 3.1.5
  (Python 3.13, `.venv`).
- Before the patch was applied, one run of the old `step5_kappa.py` overwrote the root
  `disagreements.csv` (pilot-round disagreements). It was restored from the committed version
  with `git restore -- disagreements.csv`; `git diff` shows no change. The validation
  disagreements now live only in `results/validation-30/disagreements.csv`.
- Local re-run with `.venv/bin/python`: 10 tests passed; the agreement CLI reproduced the
  figures above exactly.

## Limits
This is a focused first patch, not completion of all foundation work. Full filtering,
market data ingestion, source review, human annotation and research outcomes were not run.
Minimal validation dependencies are ranges, not a reproduction of the author's environment.
Original price cache and full SEC submissions remain on the author's machine.
Screening generation itself was not executed; its refusal behavior was exercised in an
isolated copy containing a sentinel coder file.

## Local execution
From the repository root, in a virtual environment:

```bash
python -m pip install -r requirements-validation.txt
python -m unittest discover -s tests -v
python scripts/step5_kappa.py validation_astra.csv validation_coderB_human.csv --output-dir results/validation-30
```

A second run must use a different output directory. Do not overwrite original coder files.
The screening script is not a resume-annotation command. Use existing sheets for ongoing coding.

## Next phase and coding-agent prompt

Inspect coding_manual_v3.md section 19 and validation_input.csv. Identify the 20 missing
incident/ticker keys by comparing against validation_coderB_human.csv. Prepare a blank
human-only input from validation_input.csv, preserving source links and excluding all AI
labels. Do not fill human answers or expose AI labels to the human. Preserve existing
30 answers byte-for-byte. After independent human completion, validate key uniqueness,
allowed labels and complete 50-row coverage; run step5_kappa.py into a NEW output folder.
Report category counts, confusion matrices, raw agreement, kappa and the defined adjusted
measure. Do not select or edit answers to meet the 0.6 target. Preserve independent labels
and store adjudications separately. Done means 50 valid independent human annotations plus
an auditable report, not necessarily kappa >=0.6.

## Remaining order
1. Finish blind human validation; investigate category disagreements.
2. Add data manifest and local-input checks; restore frozen price/SEC inputs locally.
3. Audit earnings coverage and unify trading-day alignment before changing POST to 10.
4. Implement reproducible all/high-confidence sample generation with explained differences.
5. Complete harm coding and independent validation before returns.
6. Resolve methods, literature and sample choices, then pre-register.
7. Implement synthetic-tested event study; run only after registration.
8. Build historical news panel and time-aware baselines/detectors; report actual false-alarm rates.
9. Write results and replication documentation from executed outputs.
