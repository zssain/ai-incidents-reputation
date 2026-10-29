"""Build the screening spreadsheet (primary + vetted recall), with date-quality
flags, a corrected-date column for coders, and a seeded pilot subset.

Columns auto-filled here are OBJECTIVE. The human-coded columns
(responsibility_type, correct_ticker, duplicate_of, keep, corrected_event_date,
reason) are left blank so two coders label independently -> Cohen's kappa.
One row per (incident, ticker) event.
"""
import json, time, os
from pathlib import Path
from output_safety import refuse_existing
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); BUILD = os.path.join(ROOT, "build")
# Check every destination before loading inputs, network calls, or writing files.
refuse_existing([Path(BUILD)/"screening_sheet.csv", Path(BUILD)/"screening_sheet.xlsx",
                 Path(ROOT)/"screening_coder_A.xlsx", Path(ROOT)/"screening_coder_B.xlsx"])
import requests
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

os.makedirs(BUILD, exist_ok=True)
exec(open(os.path.join(HERE, "step2_listed.py")).read().split("# ---- classify")[0])  # ALIASES, match, ents, df, ticker_title

# 1) PRIMARY pairs -------------------------------------------------------------
inc_tickers = {}   # iid -> {ticker: [kind, matched_entity, source]}
for _, r in df.iterrows():
    iid = int(r["Incident ID"]); hits = {}
    for name in ents(r):
        m = match(name)
        if m:
            t, kind = m
            if t not in hits or kind == "direct":
                hits[t] = [kind, name, "primary"]
    if hits:
        inc_tickers[iid] = hits

# 2) VETTED RECALL additions (title named the firm; absent from dev/deployer) ---
# produced by step3b_recall.py + manual verification (venue/common-word hits removed)
RECALL = [
    (155, "GOOGL", "google (Google Maps)"), (177, "GOOGL", "google (assistive writing)"),
    (383, "GOOGL", "google (Google Home)"), (437, "AMZN", "amazon (Amazon India search)"),
    (520, "AMZN", "amazon (Amazon Fresh cameras)"), (225, "IBM", "ibm (Watson for Oncology)"),
    (265, "UBER", "uber (Uber Eats ID checks)"), (212, "XPEV", "xpeng (facial recognition)"),
    (428, "HSBC", "hsbc (voice-ID auth)"), (613, "ADBE", "adobe (Adobe Stock)"),
]
for iid, t, ent in RECALL:
    inc_tickers.setdefault(iid, {})
    inc_tickers[iid][t] = ["direct", ent, "recall"]

ids = sorted(inc_tickers)
npairs = sum(len(v) for v in inc_tickers.values())
print(f"Incidents: {len(ids)}  |  (incident,ticker) rows: {npairs}  "
      f"(primary {sum(1 for v in inc_tickers.values() for s in v.values() if s[2]=='primary')}, "
      f"recall {len(RECALL)})")

# 3) report dates from AIID GraphQL, cached ------------------------------------
CACHE = os.path.join(BUILD, "report_dates_cache.json")
meta = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
meta = {int(k): v for k, v in meta.items()}
need = [i for i in ids if i not in meta]
if need:
    URL = "https://incidentdatabase.ai/api/graphql"
    HEAD = {"Content-Type": "application/json", "Origin": "https://incidentdatabase.ai",
            "Referer": "https://incidentdatabase.ai/",
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")}
    Q = ("query{ incidents(filter:{incident_id:{IN:[%s]}}){ incident_id date title "
         "reports{ date_published url source_domain } } }")
    for i in range(0, len(need), 40):
        chunk = need[i:i+40]
        for attempt in range(4):
            try:
                d = requests.post(URL, headers=HEAD, timeout=40,
                                  data=json.dumps({"query": Q % ",".join(map(str, chunk))})).json()["data"]["incidents"]
                for inc in d:
                    reps = sorted([r for r in inc.get("reports", []) if r.get("date_published")],
                                  key=lambda r: r["date_published"])
                    e = reps[0] if reps else None
                    meta[inc["incident_id"]] = {
                        "aiid_date": inc.get("date"), "title": inc.get("title", ""),
                        "n_reports": len(inc.get("reports", [])),
                        "earliest_report_date": e["date_published"][:10] if e else None,
                        "earliest_report_url": e["url"] if e else None,
                        "earliest_source": e.get("source_domain") if e else None}
                print(f"  fetched {min(i+40,len(need))}/{len(need)} new")
                break
            except Exception as ex:
                print("  retry:", ex); time.sleep(2+attempt*2)
    json.dump(meta, open(CACHE, "w"))

# 4) date-quality flag ---------------------------------------------------------
BLOG = ("wordpress", "blogspot", "medium.com", "substack", "tumblr", ".blog", "blogger",
        "ghost.io", "typepad", "livejournal")
def date_flag(m):
    fl = []
    er, ad = m.get("earliest_report_date"), m.get("aiid_date")
    if er and ad and er < ad:
        fl.append("before_incident")
    dom = (m.get("earliest_source") or "").lower()
    url = (m.get("earliest_report_url") or "").lower()
    if "arxiv.org" in dom or "arxiv.org" in url: fl.append("arxiv")
    if "ssrn" in dom or "ssrn" in url: fl.append("ssrn")
    if url.endswith(".pdf") or "/pdf" in url: fl.append("pdf")
    if any(x in dom or x in url for x in ("twitter.com", "x.com", "t.co", "/x.com")): fl.append("twitter/x")
    if any(b in dom or b in url for b in BLOG): fl.append("blog")
    return ";".join(fl)

# 5) assemble rows -------------------------------------------------------------
rows = []
for iid in ids:
    m = meta.get(iid, {}); n_listed = len(inc_tickers[iid]); df_flag = date_flag(m)
    for t, (kind, ent_name, source) in sorted(inc_tickers[iid].items()):
        rows.append({
            "incident_id": iid, "source": source,
            "title": (m.get("title") or "")[:120], "ticker": t,
            "company": ticker_title.get(t, "?"), "matched_entity": ent_name, "match_kind": kind,
            "aiid_incident_date": m.get("aiid_date"), "earliest_report_date": m.get("earliest_report_date"),
            "date_flag": df_flag, "earliest_report_source": m.get("earliest_source"),
            "earliest_report_url": m.get("earliest_report_url"), "n_reports": m.get("n_reports"),
            "n_listed_in_incident": n_listed, "incident_url": f"https://incidentdatabase.ai/cite/{iid}",
            # human-coded:
            "responsibility_type": "", "correct_ticker": "", "duplicate_of": "",
            "corrected_event_date": "", "keep": "", "reason": "",
        })
screen = pd.DataFrame(rows).sort_values(["incident_id", "ticker"]).reset_index(drop=True)

# 6) seeded, ticker-stratified pilot of 50 (largest-remainder allocation) -------
rng = np.random.RandomState(42)
screen["_rnd"] = rng.random(len(screen))
counts = screen["ticker"].value_counts()
quota = (50 * counts / counts.sum())
alloc = np.floor(quota).astype(int)
rem = 50 - alloc.sum()
for tk in (quota - alloc).sort_values(ascending=False).index[:rem]:
    alloc[tk] += 1
pilot_idx = []
for tk, k in alloc.items():
    if k > 0:
        pilot_idx += list(screen[screen["ticker"] == tk].sort_values("_rnd").head(k).index)
screen["pilot"] = ""
screen.loc[pilot_idx, "pilot"] = "Y"
screen = screen.drop(columns="_rnd")
print(f"Pilot rows marked: {(screen['pilot']=='Y').sum()} across {screen[screen['pilot']=='Y']['ticker'].nunique()} tickers")
print(f"date_flag set on {(screen['date_flag']!='').sum()} of {len(screen)} rows "
      f"({(screen['date_flag']!='').mean()*100:.0f}%)")

# order columns
order = ["incident_id","source","pilot","title","ticker","company","matched_entity","match_kind",
         "aiid_incident_date","earliest_report_date","date_flag","corrected_event_date",
         "earliest_report_source","earliest_report_url","n_reports","n_listed_in_incident","incident_url",
         "responsibility_type","correct_ticker","duplicate_of","keep","reason"]
screen = screen[order]
screen.to_csv(os.path.join(BUILD, "screening_sheet.csv"), index=False)
print(f"Wrote screening_sheet.csv ({len(screen)} rows)")

# 7) formatted XLSX ------------------------------------------------------------
HUMAN = {"responsibility_type","correct_ticker","duplicate_of","corrected_event_date","keep","reason"}
def build_xlsx(path, dfin):
    wb = Workbook(); ws = wb.active; ws.title = "screening"
    cols = list(dfin.columns); ws.append(cols)
    for _, r in dfin.iterrows(): ws.append([r[c] for c in cols])
    for j, c in enumerate(cols, 1):
        cell = ws.cell(1, j); cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="7030A0" if c in HUMAN else "1F4E78")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}1"
    W = {"title":48,"company":28,"matched_entity":26,"earliest_report_url":38,"incident_url":32,
         "reason":30,"earliest_report_source":18,"date_flag":16,"corrected_event_date":16}
    for j, c in enumerate(cols, 1): ws.column_dimensions[get_column_letter(j)].width = W.get(c, 13)
    n = len(dfin) + 1
    def dv(col, f):
        i = cols.index(col)+1; L = get_column_letter(i)
        v = DataValidation(type="list", formula1=f, allow_blank=True); ws.add_data_validation(v); v.add(f"{L}2:{L}{n}")
    dv("responsibility_type", '"1,2,3"'); dv("correct_ticker", '"Y,N"'); dv("keep", '"Y,N"')
    # highlight flagged dates
    warn = PatternFill("solid", fgColor="FFF2CC"); fi = cols.index("date_flag")+1
    for rr in range(2, n+1):
        if ws.cell(rr, fi).value: ws.cell(rr, fi).fill = warn
    ins = wb.create_sheet("READ ME")
    for row in [
        ["SCREENING SHEET — coding quickstart",""],["",""],
        ["Unit","one row = one (incident, listed-company) = one candidate event"],
        ["source","primary = matched on developer/deployer field; recall = firm named in title, verify carefully"],
        ["pilot","Y = code these 50 FIRST (round 1), then compute kappa & refine the manual before the rest"],
        ["You fill (purple)","responsibility_type, correct_ticker, duplicate_of, corrected_event_date, keep, reason"],
        ["responsibility_type","1=own AI failed  2=firm's tool misused by others  3=research/multi-firm study (see coding_manual_v3.md)"],
        ["correct_ticker","Y if this firm is truly the AI developer/deployer here, else N (+fix in reason)"],
        ["date_flag (yellow)","earliest_report_date may be WRONG (older background article / arxiv/ssrn/pdf/twitter/blog)."],
        ["","-> open incident_url, find the first REAL news article, put its date in corrected_event_date + note in reason"],
        ["corrected_event_date","fill ONLY when you override earliest_report_date (flagged or otherwise wrong)"],
        ["keep","Y only if type=1 AND correct_ticker=Y AND not a duplicate"],
    ]: ins.append(row)
    ins.column_dimensions["A"].width = 22; ins.column_dimensions["B"].width = 100
    for rr in range(1, 14): ins.cell(rr,1).font = Font(bold=True)
    ins.cell(1,1).font = Font(bold=True, size=14)
    wb.save(path)

build_xlsx(os.path.join(BUILD, "screening_sheet.xlsx"), screen)   # master -> build/ (keep from coders)
build_xlsx(os.path.join(ROOT, "screening_coder_A.xlsx"), screen)  # coder files -> repo root
build_xlsx(os.path.join(ROOT, "screening_coder_B.xlsx"), screen)
print("Wrote build/screening_sheet.xlsx + screening_coder_A/B.xlsx (root)")
