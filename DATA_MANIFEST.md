# Data provenance register

Baseline inspected: phase1-validation-fixes at 805db991a8805ec143668185387f89d30f98d93c.
This register distinguishes known filenames from verified acquisition metadata.

| Input | Role | Provenance status |
|---|---|---|
| data/AIID_Excel_Export-20260921.xlsx | Incident source | Filename identifies 2026-09-21 snapshot; download time and license verification still to record |
| build/screening_final.csv | Adjudicated selection | Committed derived data; retain original coder files and adjudication evidence |
| build/prices_panel.pkl | Adjusted stock price cache | Local-only; original download date, provider version, adjustment settings and market coverage not verified here |
| data/SEC EDGAR/company_tickers.json | Ticker/CIK lookup | Local snapshot; download time and historical mapping limitations to document |
| data/SEC EDGAR/submissions/ | Filing-history inputs | Local-only; check all historical files referenced by each base file |
| validation_astra.csv | Independent AI validation labels | Model identifier, version and actual run date remain unrecorded |
| validation_coderB_human.csv | Original 30 human annotations | Preserve unchanged; remaining 20 are a separate blind round completion |

Run scripts/check_local_inputs.py to create a machine-readable hash inventory for the
files used by kept candidate firms. It does not enumerate unrelated SEC files.
File modification time is not a substitute for download time. Do not invent missing
model provenance. Record "unrecorded" if original evidence cannot establish it.

A hash identifies bytes, not source quality. Presence of all referenced SEC files does
not prove complete earnings coverage. The current script uses 8-K filing dates as
proxies; they need not equal the public earnings-release timestamp. Price pickle bytes
are hashed without loading; price columns and trading-day coverage require a separate
local audit. No research returns are computed by the inventory.
