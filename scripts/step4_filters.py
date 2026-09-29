"""PRE-STAGED mechanical filters -> final event-study sample.

Run AFTER coders + adjudication produce `screening_final.csv` (keep=='Y', with
corrected_event_date filled where needed). Until then it DRY-RUNS on
screening_sheet.csv, treating every row as a candidate, so you get a provisional
attrition preview.

Filters (each logged in drop_log.csv):
  1. event_date present (corrected_event_date overrides earliest_report_date)
  2. listing / price history : ticker priced on the event date, with >=PRE trading
     days before and >=POST after  (drops delisted e.g. TuSimple, and firms not yet
     public on the event date e.g. Figma/Pony/Serve if the event predates the IPO)
  3. event merge : same ticker within +/-MERGE trading days -> collapse to one event
  4. earnings blackout : drop events within +/-EARN trading days of an earnings date
     (earnings dates = SEC 8-K item 2.02 + 10-Q/10-K filing dates, from local EDGAR)

Config below mirrors the paper's stated windows.
"""
import os, json, glob, sys
import pandas as pd, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)

PRE, POST, MERGE, EARN = 250, 5, 10, 5          # trading days
FINAL = os.path.join(BUILD, "screening_final.csv")           # place adjudicated file here
DRY = not os.path.exists(FINAL)
SRC = os.path.join(BUILD, "screening_sheet.csv") if DRY else FINAL

# ---- load candidates ---------------------------------------------------------
df = pd.read_csv(SRC)
if not DRY:
    df = df[df.get("keep").astype(str).str.upper() == "Y"]
    print(f"[FINAL RUN] {len(df)} kept events from {FINAL}")
else:
    print(f"[DRY RUN] no {FINAL} yet -> treating all {len(df)} screening rows as candidates "
          f"(provisional; real run will first drop non-kept / type!=1 rows)")

def event_date(r):
    cd = str(r.get("corrected_event_date", "")).strip()
    if cd and cd.lower() != "nan":
        return pd.to_datetime(cd, errors="coerce")
    return pd.to_datetime(r.get("earliest_report_date"), errors="coerce")

df = df.copy()
df["event_date"] = df.apply(event_date, axis=1)
drops = []
def drop(sub, reason):
    for _, r in sub.iterrows():
        drops.append({"incident_id": r["incident_id"], "ticker": r["ticker"],
                      "event_date": r.get("event_date"), "reason": reason})

# filter 1: date present
bad = df[df["event_date"].isna()]; drop(bad, "no_event_date")
df = df[df["event_date"].notna()]

# ---- prices (yfinance), cached ----------------------------------------------
tickers = sorted(df["ticker"].unique())
PX = os.path.join(BUILD, "prices_panel.pkl")
if os.path.exists(PX):
    px = pd.read_pickle(PX)
else:
    import yfinance as yf
    print(f"Downloading prices for {len(tickers)} tickers ...")
    raw = yf.download(tickers, start="2000-01-01", end="2026-09-25", auto_adjust=True, progress=False)
    px = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw
    if isinstance(px, pd.Series): px = px.to_frame(tickers[0])
    px.to_pickle(PX)
priced = set(px.columns)

def trading_index(tk):
    if tk not in priced: return None
    return px[tk].dropna().index

# filter 2: listing / history
keep_rows = []
for _, r in df.iterrows():
    idx = trading_index(r["ticker"]); ed = r["event_date"]
    if idx is None or len(idx) == 0:
        drops.append({**r[["incident_id","ticker"]].to_dict(), "event_date": ed, "reason": "no_price_data"}); continue
    before = (idx < ed).sum(); after = (idx > ed).sum()
    if ed < idx.min() or before < PRE:
        drops.append({**r[["incident_id","ticker"]].to_dict(), "event_date": ed,
                      "reason": f"insufficient_pre_history({before}<{PRE})"}); continue
    if ed > idx.max() or after < POST:
        drops.append({**r[["incident_id","ticker"]].to_dict(), "event_date": ed,
                      "reason": f"insufficient_post_history({after}<{POST})"}); continue
    keep_rows.append(r)
df = pd.DataFrame(keep_rows)
print(f"after listing/history filter: {len(df)} events")

# filter 3: event merge (same ticker within +/-MERGE trading days)
df = df.sort_values(["ticker", "event_date"]).reset_index(drop=True)
merged = []
for tk, g in df.groupby("ticker"):
    idx = trading_index(tk); last_pos = None;
    for _, r in g.iterrows():
        pos = idx.searchsorted(r["event_date"])
        if last_pos is not None and pos - last_pos <= MERGE:
            drops.append({"incident_id": r["incident_id"], "ticker": tk, "event_date": r["event_date"],
                          "reason": f"merged_with_prior(<= {MERGE}td)"}); continue
        merged.append(r); last_pos = pos
df = pd.DataFrame(merged)
print(f"after +/-{MERGE}td event merge: {len(df)} events")

# ---- earnings dates from local SEC submissions -------------------------------
tk2cik = {v["ticker"]: str(v["cik_str"]).zfill(10)
          for v in json.load(open(os.path.join(DATA, "SEC EDGAR", "company_tickers.json"))).values()}
def earnings_dates(tk):
    """Earnings-ANNOUNCEMENT dates (not report filing dates).
    US filers -> 8-K Item 2.02 (the actual release). Foreign private issuers file
    6-K/20-F and have no 8-K, so fall back to yfinance. Returns (dates, source)."""
    cik = tk2cik.get(tk); out = []
    subdir = os.path.join(DATA, "SEC EDGAR", "submissions")
    p0 = os.path.join(subdir, f"CIK{cik}.json") if cik else None
    if p0 and os.path.exists(p0):
        base = json.load(open(p0))
        blocks = [base["filings"]["recent"]]
        for extra in base["filings"].get("files", []):
            p = os.path.join(subdir, extra["name"])
            if os.path.exists(p): blocks.append(json.load(open(p)))
        for b in blocks:
            forms = b.get("form", []); fdates = b.get("filingDate", []); items = b.get("items", [""]*len(forms))
            for i, fm in enumerate(forms):
                it = items[i] if i < len(items) else ""
                if fm == "8-K" and "2.02" in str(it):        # earnings release only
                    out.append(fdates[i])
    if out:
        return pd.to_datetime(pd.Series(out), errors="coerce").dropna().sort_values().values, "sec_8k_2.02"
    try:                                                     # foreign filers / no 8-K
        import yfinance as yf
        ed = yf.Ticker(tk).get_earnings_dates(limit=80)
        if ed is not None and len(ed):
            return pd.to_datetime(pd.Series(pd.DatetimeIndex(ed.index).date)).dropna().sort_values().values, "yfinance"
    except Exception:
        pass
    return [], "none"

# filter 4: earnings blackout (+/-EARN trading days)
ecache = {tk: earnings_dates(tk) for tk in df["ticker"].unique()}
edates = {tk: v[0] for tk, v in ecache.items()}
esrc   = {tk: v[1] for tk, v in ecache.items()}
emin   = {tk: (pd.Timestamp(min(v)) if len(v) else None) for tk, v in edates.items()}
evmin  = df.groupby("ticker")["event_date"].min().to_dict()   # earliest event per firm
# log firms whose (fallback) earnings coverage does not reach their earliest event
for tk in df["ticker"].unique():
    if esrc[tk] == "sec_8k_2.02":
        continue                                              # US filer: 8-K coverage trusted
    if emin[tk] is None:
        print(f"  earnings-coverage gap: {tk} ({esrc[tk]}) returned NO earnings dates "
              f"-> its events get earn_source=none (no blackout applied)")
    elif evmin.get(tk) is not None and emin[tk] > pd.Timestamp(evmin[tk]):
        print(f"  earnings-coverage gap: {tk} earnings start {emin[tk].date()} > earliest event "
              f"{pd.Timestamp(evmin[tk]).date()} -> pre-coverage events get earn_source=none")
final_rows = []
for _, r in df.iterrows():
    tk = r["ticker"]; idx = trading_index(tk); ed = r["event_date"]; epos = idx.searchsorted(ed)
    ears = edates.get(tk, [])
    # an event is "covered" only if earnings data actually spans back to it
    covered = (esrc[tk] == "sec_8k_2.02") or (len(ears) and emin[tk] is not None and ed >= emin[tk])
    eff_src = esrc[tk] if covered else "none"
    near = covered and any(abs(idx.searchsorted(pd.Timestamp(e)) - epos) <= EARN for e in ears)
    if near:
        drops.append({"incident_id": r["incident_id"], "ticker": tk, "event_date": ed,
                      "reason": f"earnings_within_{EARN}td"})
    else:
        rr = r.copy(); rr["earn_source"] = eff_src; final_rows.append(rr)
final = pd.DataFrame(final_rows)
# robustness: which firms have no reliable earnings blackout (foreign / none)
nogb = final[final["earn_source"] != "sec_8k_2.02"]
if len(nogb):
    print(f"NOTE: {len(nogb)} final events at {nogb['ticker'].nunique()} firms lack SEC 8-K earnings "
          f"(source: {sorted(nogb['earn_source'].unique())}) -> exclude in an earnings-robustness check. "
          f"Firms: {sorted(nogb['ticker'].unique())}")
print(f"after earnings blackout: {len(final)} events")

# ---- outputs -----------------------------------------------------------------
keepcols = [c for c in ["incident_id","ticker","company","event_date","source","match_kind",
                        "responsibility_type","earn_source","title"] if c in final.columns]
final[keepcols].sort_values(["event_date","ticker"]).to_csv(os.path.join(BUILD, "final_sample.csv"), index=False)
pd.DataFrame(drops).to_csv(os.path.join(BUILD, "drop_log.csv"), index=False)
print("\n=== ATTRITION" + (" (DRY RUN — upper bound)" if DRY else "") + " ===")
print(f"  candidates in         : {len(pd.read_csv(SRC)) if not DRY else 'all rows'}")
print(f"  final events out       : {len(final)}   across {final['ticker'].nunique()} firms")
print(f"  dropped                : {len(drops)}  (see drop_log.csv)")
print(pd.DataFrame(drops)["reason"].str.replace(r"\(.*\)","",regex=True).value_counts().to_string()
      if drops else "  (none)")
print("\nWrote final_sample.csv, drop_log.csv")
if DRY:
    print("\nNOTE: DRY RUN counts every screened row. The real final N is this number "
          "intersected with coder keep=='Y' (type 1, correct_ticker=Y, non-duplicate).")
