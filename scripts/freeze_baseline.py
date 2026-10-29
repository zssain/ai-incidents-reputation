"""Freeze the current pipeline outputs and SEC inputs before any earnings-coverage repair.

  python scripts/freeze_baseline.py --name baseline-20261029

Creates snapshots/<name>/ (refuses if it exists):
  build/            byte-for-byte copy of build/, made read-only
  manifest.json     sha256 of every copied file; sha256 of the SEC files the earnings
                    filter reads (company_tickers.json + submissions files, base and
                    historical, for every keep=Y candidate firm); and, for the full SEC
                    submissions/ and companyfacts/ trees, file count, total bytes and a
                    digest of the sorted (path, size, mtime_ns) listing.
The SEC trees (~25 GB) are fingerprinted, not copied: originals stay in data/ untouched,
and any refreshed SEC data must go to a separate, dated directory.
"""
import argparse, csv, hashlib, json, os, shutil, stat, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "data" / "SEC EDGAR"

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def tree_listing(d):
    """Count, bytes and digest of the sorted (relpath, size, mtime_ns) listing."""
    rows = []
    for dirpath, _, files in os.walk(d):
        for fn in files:
            st = os.stat(os.path.join(dirpath, fn))
            rows.append((os.path.relpath(os.path.join(dirpath, fn), d), st.st_size, st.st_mtime_ns))
    rows.sort()
    h = hashlib.sha256()
    for r in rows:
        h.update(f"{r[0]}\t{r[1]}\t{r[2]}\n".encode())
    return {"files": len(rows), "bytes": sum(r[1] for r in rows),
            "max_mtime_utc": datetime.fromtimestamp(max(r[2] for r in rows) / 1e9, timezone.utc).isoformat() if rows else None,
            "listing_sha256": h.hexdigest(),
            "note": "Fingerprint of names/sizes/mtimes, not content hashes. mtime is not a download date."}

def filter_inputs():
    """SEC files step4_filters.py reads for keep=Y candidate firms."""
    with open(ROOT / "build" / "screening_final.csv", newline="") as f:
        tickers = sorted({r["ticker"].strip().upper() for r in csv.DictReader(f) if r["keep"].strip().upper() == "Y"})
    lookup = {v["ticker"].upper(): str(v["cik_str"]).zfill(10)
              for v in json.loads((SEC / "company_tickers.json").read_text()).values()}
    paths = [SEC / "company_tickers.json"]
    for t in tickers:
        base = SEC / "submissions" / f"CIK{lookup[t]}.json"
        paths.append(base)
        for extra in json.loads(base.read_text())["filings"].get("files", []):
            paths.append(SEC / "submissions" / extra["name"])
    return tickers, paths

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    out = ROOT / "snapshots" / args.name
    if out.exists():
        ap.error(f"{out} exists; choose a new name")
    shutil.copytree(ROOT / "build", out / "build")
    copied = sorted(p for p in (out / "build").rglob("*") if p.is_file())
    for p in copied:
        if sha256(p) != sha256(ROOT / "build" / p.relative_to(out / "build")):
            raise RuntimeError(f"copy mismatch: {p}")
    tickers, sec_paths = filter_inputs()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_head": head,
        "purpose": "Baseline before earnings-coverage repair; filters, sample and annotations unchanged.",
        "build_copy": [{"path": str(p.relative_to(out)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in copied],
        "aiid_export": {"path": "data/AIID_Excel_Export-20260921.xlsx",
                        "sha256": sha256(ROOT / "data" / "AIID_Excel_Export-20260921.xlsx")},
        "sec_filter_inputs": {"candidate_tickers": len(tickers),
                              "files": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)}
                                        for p in sec_paths]},
        "sec_trees": {name: tree_listing(SEC / name) for name in ("submissions", "companyfacts")},
        "unrecorded": ["SEC download date", "price download date and adjustment settings",
                       "AI coder model/version/run date"],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    for p in copied + [out / "manifest.json"]:
        p.chmod(p.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    print(f"Froze {len(copied)} build files and {len(sec_paths)} SEC filter inputs "
          f"({len(tickers)} candidate firms) into {out}")
    for k, v in manifest["sec_trees"].items():
        print(f"  {k}: {v['files']} files, {v['bytes']/1e9:.1f} GB, listing {v['listing_sha256'][:16]}")

if __name__ == "__main__":
    main()
