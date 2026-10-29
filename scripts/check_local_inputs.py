"""Offline provenance inventory. Never downloads, unpickles, or modifies source data."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

REQUIRED = ['data/AIID_Excel_Export-20260921.xlsx', 'build/screening_final.csv',
            'build/prices_panel.pkl', 'data/SEC EDGAR/company_tickers.json']

def fingerprint(path, root):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': h.hexdigest()}

def inventory(root):
    root = Path(root).resolve()
    report = {'scope': 'Local file availability and provenance only; not earnings or price coverage certification',
              'files': [], 'issues': [], 'firms': [], 'unknown_provenance':
              ['AI coder model/version/run date', 'SEC snapshot/download date', 'price download date', 'price adjustment settings']}
    seen = set()
    def record(path):
        if path not in seen:
            report['files'].append(fingerprint(path, root)); seen.add(path)
    for rel in REQUIRED:
        path = root / rel
        if path.is_file(): record(path)
        else: report['issues'].append(f'Missing required file: {rel}')
    screen = root / 'build/screening_final.csv'
    mapping = root / 'data/SEC EDGAR/company_tickers.json'
    if not screen.is_file() or not mapping.is_file():
        return report
    try:
        with screen.open(newline='') as f:
            reader = csv.DictReader(f)
            if not {'ticker','keep'} <= set(reader.fieldnames or []):
                raise ValueError('screening_final.csv needs ticker and keep columns')
            tickers = sorted({r['ticker'].strip().upper() for r in reader if r['keep'].strip().upper() == 'Y'})
        data = json.loads(mapping.read_text())
        lookup = {r['ticker'].upper(): str(int(r['cik_str'])).zfill(10) for r in data.values()}
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        report['issues'].append(f'Invalid screening or ticker mapping: {e}')
        return report
    directory = root / 'data/SEC EDGAR/submissions'
    for ticker in tickers:
        row = {'ticker': ticker, 'cik': lookup.get(ticker), 'missing_history': [], 'status': 'unresolved'}
        report['firms'].append(row)
        if row['cik'] is None:
            report['issues'].append(f'{ticker}: no CIK mapping'); continue
        base = directory / ('CIK' + row['cik'] + '.json')
        if not base.is_file():
            report['issues'].append(f'{ticker}: missing base submissions file'); continue
        record(base)
        try:
            content = json.loads(base.read_text())
            filings = content['filings']
            blocks = [filings['recent']]
            for extra in filings.get('files', []):
                name = extra['name']
                if not isinstance(name, str) or Path(name).name != name:
                    raise ValueError('Invalid historical filename')
                path = directory / name
                if not path.is_file(): row['missing_history'].append(name)
                else:
                    record(path); blocks.append(json.loads(path.read_text()))
            dates = []; count = 0
            for block in blocks:
                forms, ds = block['form'], block['filingDate']
                items = block.get('items')
                if len(forms) != len(ds) or items is None or len(items) != len(forms):
                    raise ValueError('Missing or unequal form/filingDate/items arrays')
                dates.extend(d for d in ds if d)
                count += sum(f == '8-K' and '2.02' in str(i) for f,i in zip(forms,items))
            row.update(qualifying_records=count, filing_date_min=min(dates) if dates else None,
                       filing_date_max=max(dates) if dates else None,
                       status='missing_history' if row['missing_history'] else 'referenced_files_present')
            if row['missing_history']: report['issues'].append(f'{ticker}: missing referenced historical files')
        except (ValueError, KeyError, TypeError) as e:
            report['issues'].append(f'{ticker}: invalid submissions structure: {e}')
    return report

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists(): ap.error('Output exists; choose a new filename')
    result = inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f: json.dump(result, f, indent=2)
    print(f"Recorded {len(result['files'])} files and {len(result['issues'])} issues. See {args.output}")
    return 2 if result['issues'] else 0

if __name__ == '__main__': raise SystemExit(main())
