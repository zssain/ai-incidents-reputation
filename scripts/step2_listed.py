"""GO/NO-GO CHECK: how many AIID incidents involve a *publicly listed* company?

Method
------
1. Extract the deployer/developer entities for each incident (incident-level sets).
2. Match each entity to a US-listed issuer using:
     (a) a curated alias map  -> handles brands / former names / subsidiaries
         whose *listed* entity is the parent (youtube -> GOOGL, facebook -> META, ...)
     (b) strict normalised EXACT match against SEC company_tickers.json (10,419 tickers)
         -> catches the long tail (netflix, nvidia, ...) with high precision.
   Genuinely private firms (OpenAI, Anthropic, xAI, TikTok/ByteDance, X/Twitter,
   Clearview, Character.AI, ...) do NOT match and are correctly excluded.
3. Count incidents that involve >=1 listed company.
   - STRICT  : entity IS the listed issuer / its universal brand (tesla, apple, google, meta...)
   - LENIENT : also folds subsidiaries & products into the listed parent (waymo->GOOGL, zoox->AMZN...)
"""

import os, json, re
import pandas as pd
from collections import Counter, defaultdict

# repo-root-relative paths (scripts/ is one level below root) -> run from anywhere
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)

AIID = os.path.join(DATA, "AIID_Excel_Export-20260921.xlsx")
SEC = os.path.join(DATA, "SEC EDGAR", "company_tickers.json")

# ---- curated alias map: AIID entity name -> (ticker, kind) --------------------
# kind: "direct"  = the entity is itself the listed issuer (or its universal brand)
#       "subsid"  = entity is a subsidiary/product; listed exposure is the parent
ALIASES = {
    # --- direct: brand == listed issuer ---
    "google": ("GOOGL", "direct"), "meta": ("META", "direct"),
    "facebook": ("META", "direct"), "tesla": ("TSLA", "direct"),
    "microsoft": ("MSFT", "direct"), "amazon": ("AMZN", "direct"),
    "apple": ("AAPL", "direct"), "uber": ("UBER", "direct"),
    "walmart": ("WMT", "direct"), "target": ("TGT", "direct"),
    "ibm": ("IBM", "direct"), "snapchat": ("SNAP", "direct"), "snap": ("SNAP", "direct"),
    "paypal": ("PYPL", "direct"), "alibaba": ("BABA", "direct"),
    "baidu": ("BIDU", "direct"), "mcdonald's": ("MCD", "direct"),
    "lockheed martin": ("LMT", "direct"), "raytheon": ("RTX", "direct"),
    "thomson reuters": ("TRI", "direct"), "integra lifesciences": ("IART", "direct"),
    "evolv technology": ("EVLV", "direct"), "serve robotics": ("SERV", "direct"),
    "knightscope": ("KSCP", "direct"), "shotspotter": ("SSTI", "direct"),
    "general motors": ("GM", "direct"),
    # --- subsidiary / product -> listed parent ---
    "youtube": ("GOOGL", "subsid"), "waymo": ("GOOGL", "subsid"),
    "waze": ("GOOGL", "subsid"), "gemini": ("GOOGL", "subsid"),
    "google bard": ("GOOGL", "subsid"), "google bard": ("GOOGL", "subsid"),
    "google deepmind": ("GOOGL", "subsid"), "google gemini": ("GOOGL", "subsid"),
    "instagram": ("META", "subsid"), "whatsapp": ("META", "subsid"),
    "linkedin": ("MSFT", "subsid"), "microsoft copilot": ("MSFT", "subsid"),
    "bing": ("MSFT", "subsid"),
    "zoox": ("AMZN", "subsid"),
    "cruise": ("GM", "subsid"),
    "acclarent": ("JNJ", "subsid"), "navihealth": ("UNH", "subsid"),
}

# entities that share a normalised form with some SEC filer but are NOT that
# company (private firms, delisted names) -> block false auto-matches.
BLOCK_AUTO = {
    "openai", "anthropic", "xai", "twitter", "x (twitter)", "tiktok", "chatgpt",
    "clearview ai", "character.ai", "stability ai", "perplexity", "perplexity ai",
    "runway", "replika", "midjourney", "mistral", "deepseek", "deepseek ai",
    "you.com", "inflection", "leonardo ai", "grammarly", "deloitte", "cnet",
    "turnitin", "synthesia", "realpage", "hirevue", "state farm", "faceapp",
    "wechat", "bytedance", "megvii", "ntechlab", "pimeyes", "boston dynamics",
    "springer nature", "otter.ai", "chai", "gaggle", "proctorio", "proctoru",
    "userway", "gptzero", "lensa ai", "nomi ai", "janitorai", "crushon.ai",
    "cursor", "anysphere", "nous research", "chatgpt users", "grok",
    "employers", "minimax",   # generic word / private Chinese AI lab (not the SEC filers)
}

SUFFIX = {"inc","corp","corporation","co","company","ltd","limited","llc","lp",
          "plc","sa","ag","nv","se","holdings","holding","the","adr","group",
          "com","cl","class","a","b"}

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"/[a-z]{2,4}/?", " ", s)   # drop SEC trailing codes: /de/ /can/ /md/ /adr
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t and t not in SUFFIX]
    return " ".join(toks)

# ---- build SEC listed lookup -------------------------------------------------
sec = json.load(open(SEC))
sec_items = list(sec.values())
ticker_title = {x["ticker"]: x["title"] for x in sec_items}
sec_norm = {}                       # normalised title -> ticker (first wins)
for x in sec_items:
    k = norm(x["title"])
    if k and k not in sec_norm:
        sec_norm[k] = x["ticker"]

# sanity-check every alias ticker actually exists in SEC file
missing = sorted({t for t,_ in ALIASES.values()} - set(ticker_title))
if missing:
    print("WARNING: alias tickers not found in SEC file:", missing)

# ---- load incidents ----------------------------------------------------------
df = pd.read_excel(AIID, sheet_name="Incidents", header=2)
df = df[df["Incident ID"].notna()]
def ents(row):
    s = set()
    for c in ["deployer", "developer"]:
        v = str(row[c])
        if v and v.lower() != "nan":
            for n in v.replace(";", ",").split(","):
                n = n.strip().strip("[]'\"").lower()
                if n:
                    s.add(n)
    return s

def match(name):
    """return (ticker, kind) or None"""
    if name in ALIASES:
        return ALIASES[name]
    if name in BLOCK_AUTO:
        return None
    k = norm(name)
    if k and k in sec_norm:
        return (sec_norm[k], "direct")   # auto exact match
    return None

# ---- classify incidents ------------------------------------------------------
strict_inc = 0          # >=1 direct-listed entity
lenient_inc = 0         # >=1 direct OR subsidiary-of-listed entity
listed_company_incidents = Counter()   # ticker -> #incidents (lenient)
auto_matches = {}       # name -> ticker (from exact match, for review)
matched_names_kind = {}
total = len(df)

for _, r in df.iterrows():
    e = ents(r)
    tickers_here = {}   # ticker -> kind (strongest: direct beats subsid)
    for name in e:
        m = match(name)
        if m:
            t, kind = m
            if name not in ALIASES and name not in BLOCK_AUTO:
                auto_matches[name] = t
            matched_names_kind[name] = kind
            if t not in tickers_here or kind == "direct":
                tickers_here[t] = kind
    if tickers_here:
        lenient_inc += 1
        for t in tickers_here:
            listed_company_incidents[t] += 1
        if any(k == "direct" for k in tickers_here.values()):
            strict_inc += 1

# ---- report ------------------------------------------------------------------
print("="*70)
print(f"Total incidents in AIID export        : {total}")
print(f"Incidents involving a LISTED company")
print(f"  STRICT  (entity is the issuer/brand): {strict_inc}  ({strict_inc/total*100:.1f}%)")
print(f"  LENIENT (incl. subsidiaries->parent): {lenient_inc}  ({lenient_inc/total*100:.1f}%)")
print("="*70)

rows = []
for t, c in listed_company_incidents.most_common():
    rows.append({"ticker": t, "company": ticker_title.get(t, "?"), "incidents": c})
out = pd.DataFrame(rows)
out.to_csv(os.path.join(BUILD, "listed_company_incidents.csv"), index=False)
print(f"\nListed companies by #incidents (lenient) -> listed_company_incidents.csv")
print(out.to_string(index=False))

print("\nAuto (exact-match) hits beyond the curated aliases, for review:")
for n, t in sorted(auto_matches.items()):
    print(f"   {n}  ->  {t}  ({ticker_title.get(t)})")
