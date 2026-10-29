"""Blank human-coding sheet for the validation rows not yet coded by the human coder.

  python scripts/make_validation_remaining.py

Selects rows of validation_input.csv whose (incident_id, ticker) key is missing from
validation_coderB_human.csv -- by key, not row position. Copies only source columns from
validation_input.csv (no AI answers, disagreements or adjudications) and leaves the human
coding fields blank. Refuses to overwrite an existing output. Inputs are read, never written.
"""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from output_safety import refuse_existing

INPUT = os.path.join(ROOT, "validation_input.csv")            # 50 drawn rows, source info only
DONE = os.path.join(ROOT, "validation_coderB_human.csv")      # 30 completed human rows
OUT = os.path.join(ROOT, "validation_remaining20_human.csv")
EXPECTED_TOTAL, EXPECTED_DONE = 50, 30

SOURCE_COLS = ["incident_id", "ticker", "company", "title", "aiid_incident_date",
               "earliest_report_date", "date_flag", "incident_url"]
HUMAN_COLS = ["responsibility_type", "correct_ticker", "duplicate_of",
              "corrected_event_date", "keep", "reason"]     # same fields as the completed 30

def keys(d):
    k = list(zip(d["incident_id"].astype(int), d["ticker"].astype(str).str.strip().str.upper()))
    if len(set(k)) != len(k):
        raise ValueError("duplicate incident_id/ticker key")
    return k

def main():
    refuse_existing([OUT])
    vi, done = pd.read_csv(INPUT), pd.read_csv(DONE)
    vk, dk = keys(vi), set(keys(done))
    if len(vk) != EXPECTED_TOTAL or len(dk) != EXPECTED_DONE:
        raise ValueError(f"expected {EXPECTED_TOTAL} input / {EXPECTED_DONE} done keys, got {len(vk)} / {len(dk)}")
    if not dk <= set(vk):
        raise ValueError(f"completed keys not in validation_input.csv: {sorted(dk - set(vk))}")

    rem = vi[[k not in dk for k in vk]][SOURCE_COLS].copy()
    for c in HUMAN_COLS:
        rem[c] = ""
    rk = set(keys(rem))
    assert len(rk) == EXPECTED_TOTAL - EXPECTED_DONE, len(rk)
    assert not (rk & dk), "overlap with completed rows"
    assert rk | dk == set(vk), "combined coverage != original 50"

    rem.to_csv(OUT, index=False)
    print(f"Wrote {OUT}: {len(rem)} rows, {len(rk)} unique keys, 0 overlap with the completed "
          f"{len(dk)}, combined coverage {len(rk | dk)}/{len(vk)}")

if __name__ == "__main__":
    main()
