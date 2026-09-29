"""Download adjusted daily close prices from Yahoo Finance and cache to prices.csv.

auto_adjust=True -> 'Close' is already adjusted for splits & dividends, which is
what you want for computing returns. Yahoo can rate-limit repeated requests, so
this downloads once and reuses the CSV on subsequent runs (delete prices.csv or
pass --force to refresh).
"""

import argparse
import sys

import pandas as pd
import yfinance as yf

TICKERS = ["GOOGL", "MSFT", "TSLA", "^GSPC"]  # ^GSPC = S&P 500 index
START = "2015-01-01"
END = "2026-09-01"
OUT = "prices.csv"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="re-download even if prices.csv exists")
    args = ap.parse_args()

    from pathlib import Path

    if Path(OUT).exists() and not args.force:
        print(f"{OUT} already exists; loading it (use --force to re-download).")
        close = pd.read_csv(OUT, index_col=0, parse_dates=True)
    else:
        print(f"Downloading {TICKERS} from {START} to {END} ...")
        data = yf.download(TICKERS, start=START, end=END, auto_adjust=True, progress=False)
        if data is None or data.empty:
            print("ERROR: no data returned (Yahoo may be rate-limiting).", file=sys.stderr)
            return 1
        # With multiple tickers, columns are a MultiIndex (field, ticker).
        close = data["Close"] if "Close" in data.columns.get_level_values(0) else data
        # Keep a stable column order matching TICKERS where present.
        cols = [t for t in TICKERS if t in close.columns]
        close = close[cols] if cols else close
        close.to_csv(OUT)
        print(f"Saved adjusted close prices -> {OUT}")

    print(f"\nShape: {close.shape[0]} rows x {close.shape[1]} cols")
    print(f"Date range: {close.index.min().date()} -> {close.index.max().date()}")
    print(f"Columns: {list(close.columns)}")
    print("\nMissing values per column:")
    print(close.isna().sum().to_string())
    print("\nHead:")
    print(close.head().to_string())
    print("\nTail:")
    print(close.tail().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
