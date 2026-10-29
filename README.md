# AI Incidents × Listed Companies — event-study screening

**Coders: only touch the files in this top folder.**

1. **Coder A** → open `screening_coder_A.xlsx`. **Coder B** → open `screening_coder_B.xlsx`.
2. Read `coding_manual_v3.md` first and agree on the rules.
3. Code the **50 `pilot=Y` rows first** (independently, no discussion), then send both files back.
4. Fill only the purple columns: `responsibility_type, correct_ticker, duplicate_of, corrected_event_date, keep, reason`.

## Folder layout
- `/` — coder files + manual + this README (coders look only here)
- `scripts/` — pipeline (`step2`→`step5`); run from repo root, e.g. `.venv/bin/python scripts/step4_filters.py`
- `build/` — master `screening_sheet.xlsx/.csv`, caches, and dry-run outputs (keep away from coders)
- `data/` — `AIID_Excel_Export-20260921.xlsx`, `SEC EDGAR/`

## Pipeline order
`step2_listed.py` (match listed firms) → `step3b_recall.py` (recall missed firms) →
`step3_screening.py` (build screening sheet) → coders code → `step5_kappa.py` A B [--pilot] (κ) →
adjudicate into `build/screening_final.csv` → `step4_filters.py` (final sample).


## Phase 1: safe validation

Use Python 3.11+ with pandas and openpyxl installed. The original environment is
not available here; these are minimal validation dependencies, not a full lockfile.

```bash
python -m pip install -r requirements-validation.txt
python -m unittest discover -s tests -v
python scripts/step5_kappa.py validation_astra.csv validation_coderB_human.csv --output-dir results/validation-30
```

Choose a new output directory for each run. Outputs include metrics, confusion
matrices and disagreements. Missing annotations are excluded per field; unmatched
keys are printed. Undefined kappa is blank, never interpreted as perfect agreement.
The uniform-chance adjusted statistic uses `(q * agreement - 1)/(q - 1)`, with
q=3 for responsibility type and q=2 for binary fields. It does not replace the
manual's kappa target. Preserve original independent labels before adjudication.

Screening generation refuses existing master or coder outputs before any work.
Use a separate working copy for regenerating blank templates. Do not delete
completed annotations to bypass this protection.

See docs/phase1_status.md for checks, limitations and next steps.
