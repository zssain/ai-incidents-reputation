# AI Incidents × Listed Companies — event-study screening

**Coders: only touch the files in this top folder.**

1. **Coder A** → open `screening_coder_A.xlsx`. **Coder B** → open `screening_coder_B.xlsx`.
2. Read `coding_manual.md` first and agree on the rules.
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
