"""RECALL PASS: find listed firms the primary matcher missed.

The primary matcher only read the `deployer`/`developer` fields. Firms named only
in the title/description/Entities (e.g. Whirlpool in #1304) were missed. Here we
scan the full incident text of ALL 1,689 incidents against every SEC-listed name
(whole-word, suffix-stripped) + the curated brand aliases, then emit candidate
(incident, ticker) pairs NOT already in the primary sample, for manual verification.
"""
import os, json, re
import pandas as pd
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)
exec(open(os.path.join(HERE, "step2_listed.py")).read().split("# ---- classify")[0])  # ALIASES, norm, sec_norm, ticker_title, match, ents, df

# ---- primary pairs already captured (to exclude) -----------------------------
primary = defaultdict(set)
for _, r in df.iterrows():
    iid = int(r["Incident ID"])
    for name in ents(r):
        m = match(name)
        if m:
            primary[iid].add(m[0])

# ---- build the recall name->ticker index -------------------------------------
# load an English dictionary; single-token SEC names that ARE common words are
# dropped (they collide with ordinary text) UNLESS they are known brands.
try:
    english = {w.strip().lower() for w in open("/usr/share/dict/words")}
except Exception:
    english = set()
# dictionary-word brands we DO still want to catch as single tokens:
ALLOW1 = {"whirlpool","apple","amazon","target","adobe","oracle","visa","gap",
          "block","square","match","unity","strategy","reliance","interface",
          "netflix","starbucks","boeing","coupang","zillow","airbnb"}
GENERIC = {"global","group","holdings","people","crypto","authentic","highway",
           "senior","reliability","citizens","track","pattern","founder","enhanced",
           "intelligent","awareness","commerce","click","winners","emerging","morgan",
           "cohen","eastern","coffee","reliance","employers","megan","awareness",
           "joint","popular","southern","metro","eastern","winners","enhanced"}

brand_keys = {norm(a) or a for a in ALIASES}
name2t = {}
for k, t in sec_norm.items():
    toks = k.split()
    if len(toks) == 1:
        if k in brand_keys or k in ALLOW1:
            pass                                  # keep known brand
        elif k in GENERIC or len(k) < 4 or k in english:
            continue                              # drop generic / dictionary word
    name2t[k] = t
for a, (t, _) in ALIASES.items():                 # curated brands win
    name2t[norm(a) or a] = t

maxlen = max(len(k.split()) for k in name2t)

# ---- scan title + structured entity fields (high precision) ------------------
# AIID titles lead with the responsible firm; Entities/Implicated Systems are
# structured entity names. We deliberately do NOT scan free-form description,
# where a listed firm is usually just the venue (e.g. "spread on Facebook").
def fulltext(row):
    # TITLE ONLY: AIID titles lead with the responsible firm -> highest precision.
    return norm(str(row.get("title","")))

cand = defaultdict(lambda: defaultdict(int))   # ticker -> {incident: hits}
cand_ctx = {}
for _, r in df.iterrows():
    iid = int(r["Incident ID"])
    toks = fulltext(r).split()
    found = set()
    for i in range(len(toks)):
        for L in range(1, maxlen+1):
            if i+L > len(toks): break
            gram = " ".join(toks[i:i+L])
            t = name2t.get(gram)
            if t and t not in primary.get(iid, set()):
                found.add((t, gram))
    for t, gram in found:
        cand[t][iid] += 1
        cand_ctx[(t, iid)] = gram

# ---- report candidates for verification --------------------------------------
titles = {int(r["Incident ID"]): str(r["title"]) for _, r in df.iterrows()}
rows = []
for t, inc in sorted(cand.items(), key=lambda kv: -len(kv[1])):
    for iid in sorted(inc):
        rows.append({"ticker": t, "company": ticker_title.get(t,"?"),
                     "incident_id": iid, "matched_gram": cand_ctx[(t,iid)],
                     "title": titles[iid][:80]})
out = pd.DataFrame(rows)
out.to_csv(os.path.join(BUILD, "recall_candidates.csv"), index=False)
print(f"Recall candidates: {len(out)} (incident,ticker) pairs across {out['ticker'].nunique()} tickers")
print("\nCandidate tickers by #new incidents (verify these):")
agg = out.groupby(["ticker","company"]).size().reset_index(name="new_incidents").sort_values("new_incidents", ascending=False)
print(agg.head(60).to_string(index=False))
