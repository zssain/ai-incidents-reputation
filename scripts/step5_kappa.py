"""Cohen's kappa for two independent coders. Run after each coding round.

  python step5_kappa.py screening_coder_A.xlsx screening_coder_B.xlsx           # full
  python step5_kappa.py screening_coder_A.xlsx screening_coder_B.xlsx --pilot   # pilot only

Reports kappa + % agreement for responsibility_type (headline), correct_ticker,
and keep, on rows BOTH coders labeled, and writes disagreements.csv to adjudicate.
"""
import sys
import argparse
from pathlib import Path
import pandas as pd

# incidents used as WORKED EXAMPLES in coding_manual_v3.md Appendix A -> excluded from kappa
# (coders may copy the manual's answer, which would inflate agreement). State this in the paper.
# NOTE: updated for v3 Appendix A. (Old set also listed 225, which is in no appendix version;
# dropped here. Re-add it if that exclusion was intentional.)
MANUAL_EXAMPLE_IDS = {1, 3, 4, 6, 10, 12, 13, 14, 102, 189, 261, 293, 475, 574, 587, 1210,
                      1218, 1220, 1302, 1304, 1393, 1436, 1510, 1528, 1534, 1588, 1589, 1679}

def nz(s):
    """Normalise a label cell so cosmetic differences don't count as disagreement:
    Excel's '1.0' -> '1', and yes/no -> Y/N."""
    s = str(s).strip().upper()
    if s.endswith(".0"): s = s[:-2]
    return {"YES": "Y", "NO": "N"}.get(s, s)

def load(p):
    d = pd.read_excel(p) if p.endswith((".xlsx", ".xls")) else pd.read_csv(p)
    required = {"incident_id", "ticker", "responsibility_type", "correct_ticker", "keep"}
    missing = required - set(d.columns)
    if missing:
        raise ValueError(f"{p}: missing columns {sorted(missing)}")
    ids = pd.to_numeric(d["incident_id"], errors="raise")
    if ids.isna().any() or (ids % 1 != 0).any():
        raise ValueError(f"{p}: incident IDs must be nonblank integers")
    d["incident_id"] = ids.astype(int)
    if d["ticker"].isna().any():
        raise ValueError(f"{p}: missing ticker")
    d["ticker"] = d["ticker"].astype(str).str.strip().str.upper()
    if d["ticker"].eq("").any() or d.duplicated(["incident_id", "ticker"]).any():
        raise ValueError(f"{p}: blank ticker or duplicate incident/ticker key")
    for field, allowed in [("responsibility_type", {"1", "2", "3"}), ("correct_ticker", {"Y", "N"}), ("keep", {"Y", "N"})]:
        d[field] = d[field].map(lambda v: nz(v) if pd.notna(v) and str(v).strip() else pd.NA)
        if not set(d[field].dropna()).issubset(allowed):
            raise ValueError(f"{p}: invalid labels in {field}")
    d["_key"] = d["incident_id"].astype(str) + "|" + d["ticker"].astype(str)
    return d

def kappa(a, b):
    """Cohen's kappa for two equal-length label lists."""
    if len(a) != len(b):
        raise ValueError("Coder label lists must have equal lengths")
    cats = sorted(set(a) | set(b)); n = len(a)
    if n == 0: return float("nan"), float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((sum(x == c for x in a)/n) * (sum(y == c for y in b)/n) for c in cats)
    k = (po - pe) / (1 - pe) if pe != 1 else float("nan")
    return k, po

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coder_a")
    parser.add_argument("coder_b")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output-dir", required=True, help="New directory; existing paths are refused")
    args = parser.parse_args()
    out = Path(args.output_dir)
    if out.exists():
        parser.error("Output directory exists; choose a new directory to preserve previous results")
    A, B = load(args.coder_a), load(args.coder_b)
    pilot = args.pilot
    if pilot:
        if "pilot" not in A:
            raise ValueError("--pilot requires a pilot column in coder A")
        keys = set(A[A.get("pilot").astype(str).str.upper() == "Y"]["_key"])
        A, B = A[A["_key"].isin(keys)], B[B["_key"].isin(keys)]
        print(f"[PILOT] {len(keys)} pilot rows")
    m = A.merge(B, on="_key", suffixes=("_A", "_B"), validate="one_to_one")
    ex = m["incident_id_A"].isin(MANUAL_EXAMPLE_IDS)
    if ex.any():
        print(f"excluding {ex.sum()} manual-example rows from kappa (incidents {sorted(set(m.loc[ex,'incident_id_A']))})")
        m = m[~ex]
    print(f"aligned rows: {len(m)}\n")
    print(f"Unmatched keys: coder A={len(set(A._key)-set(B._key))}, coder B={len(set(B._key)-set(A._key))}")
    dis = []
    metrics = []
    out.mkdir(parents=True, exist_ok=False)
    for f in ["responsibility_type", "correct_ticker", "keep"]:
        ca, cb = f+"_A", f+"_B"
        sub = m[m[ca].notna() & m[cb].notna()].copy()
        if sub.empty:
            print(f"{f:20} : no labeled rows yet"); continue
        a = [nz(x) for x in sub[ca].tolist()]
        b = [nz(x) for x in sub[cb].tolist()]
        k, po = kappa(a, b)
        q = 3 if f == "responsibility_type" else 2
        metrics.append({"field": f, "n": len(sub), "agreement": po, "kappa": k,
                        "category_count": q, "uniform_chance_adjusted_agreement": (q*po-1)/(q-1)})
        pd.crosstab(pd.Series(a, name="coder_A"), pd.Series(b, name="coder_B")).to_csv(out / (f + "_confusion.csv"))
        tag = ("EXCELLENT" if k >= .8 else "good" if k >= .6 else "WEAK — refine manual")
        print(f"{f:20} : kappa={k:.3f}  agreement={po*100:4.0f}%  n={len(sub):4d}   {tag}")
        d = sub[[x != y for x, y in zip(a, b)]]
        for _, r in d.iterrows():
            dis.append({"key": r["_key"], "field": f, "coder_A": r[ca], "coder_B": r[cb],
                        "title": str(r.get("title_A", ""))[:70]})
    pd.DataFrame(dis, columns=["key", "field", "coder_A", "coder_B", "title"]).to_csv(out / "disagreements.csv", index=False)
    pd.DataFrame(metrics).to_csv(out / "metrics.csv", index=False)
    print(f"Outputs: {out}. Undefined kappa is saved blank; inspect raw agreement and class counts.")
    print("\nTarget: responsibility_type kappa >= 0.6 (ideally >= 0.7) before the full round.")

if __name__ == "__main__":
    main()
