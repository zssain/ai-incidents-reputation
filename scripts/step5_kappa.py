"""Cohen's kappa for two independent coders. Run after each coding round.

  python step5_kappa.py screening_coder_A.xlsx screening_coder_B.xlsx           # full
  python step5_kappa.py screening_coder_A.xlsx screening_coder_B.xlsx --pilot   # pilot only

Reports kappa + % agreement for responsibility_type (headline), correct_ticker,
and keep, on rows BOTH coders labeled, and writes disagreements.csv to adjudicate.
"""
import sys
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
    d["_key"] = d["incident_id"].astype(str) + "|" + d["ticker"].astype(str)
    return d

def kappa(a, b):
    """Cohen's kappa for two equal-length label lists."""
    cats = sorted(set(a) | set(b)); n = len(a)
    if n == 0: return float("nan"), 0
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((sum(x == c for x in a)/n) * (sum(y == c for y in b)/n) for c in cats)
    k = (po - pe) / (1 - pe) if pe != 1 else 1.0
    return k, po

def main():
    A, B = load(sys.argv[1]), load(sys.argv[2])
    pilot = "--pilot" in sys.argv
    if pilot:
        keys = set(A[A.get("pilot").astype(str).str.upper() == "Y"]["_key"])
        A, B = A[A["_key"].isin(keys)], B[B["_key"].isin(keys)]
        print(f"[PILOT] {len(keys)} pilot rows")
    m = A.merge(B, on="_key", suffixes=("_A", "_B"))
    ex = m["incident_id_A"].isin(MANUAL_EXAMPLE_IDS)
    if ex.any():
        print(f"excluding {ex.sum()} manual-example rows from kappa (incidents {sorted(set(m.loc[ex,'incident_id_A']))})")
        m = m[~ex]
    print(f"aligned rows: {len(m)}\n")
    dis = []
    for f in ["responsibility_type", "correct_ticker", "keep"]:
        ca, cb = f+"_A", f+"_B"
        sub = m[m[ca].notna() & m[cb].notna()].copy()
        if sub.empty:
            print(f"{f:20} : no labeled rows yet"); continue
        a = [nz(x) for x in sub[ca].tolist()]
        b = [nz(x) for x in sub[cb].tolist()]
        k, po = kappa(a, b)
        tag = ("EXCELLENT" if k >= .8 else "good" if k >= .6 else "WEAK — refine manual")
        print(f"{f:20} : kappa={k:.3f}  agreement={po*100:4.0f}%  n={len(sub):4d}   {tag}")
        d = sub[[x != y for x, y in zip(a, b)]]
        for _, r in d.iterrows():
            dis.append({"key": r["_key"], "field": f, "coder_A": r[ca], "coder_B": r[cb],
                        "title": str(r.get("title_A", ""))[:70]})
    if dis:
        pd.DataFrame(dis).to_csv("disagreements.csv", index=False)
        print(f"\n{len(dis)} disagreements -> disagreements.csv (adjudicate these)")
    print("\nTarget: responsibility_type kappa >= 0.6 (ideally >= 0.7) before the full round.")

if __name__ == "__main__":
    main()
