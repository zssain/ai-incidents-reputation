import sys, tempfile, unittest, json, ast
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_local_inputs import inventory

class InputTests(unittest.TestCase):
    def test_missing(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(len(inventory(t)['issues']),4)
    def fixture(self, root, history=False):
        (root/'data/SEC EDGAR/submissions').mkdir(parents=True)
        (root/'build').mkdir()
        (root/'data/AIID_Excel_Export-20260921.xlsx').write_bytes(b'synthetic')
        (root/'build/prices_panel.pkl').write_bytes(b'not a pickle: must only hash')
        (root/'build/screening_final.csv').write_text('ticker,keep\nABC,Y\n')
        (root/'data/SEC EDGAR/company_tickers.json').write_text(json.dumps({'0':{'ticker':'ABC','cik_str':1}}))
        block={'form':['8-K','10-Q'],'filingDate':['2020-01-01','2020-02-01'],'items':['2.02','']}
        base={'filings':{'recent':block,'files':[{'name':'old.json'}] if history else []}}
        path=root/'data/SEC EDGAR/submissions/CIK0000000001.json';path.write_text(json.dumps(base))
        return path
    def test_hash_only_and_present(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.fixture(root);r=inventory(root)
            self.assertEqual(r['issues'],[]); self.assertEqual(r['firms'][0]['qualifying_records'],1)
            self.assertTrue(all(len(f['sha256'])==64 for f in r['files']))
    def test_missing_history(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.fixture(root,True);r=inventory(root)
            self.assertEqual(r['firms'][0]['missing_history'],['old.json'])
    def test_companyfacts_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=self.fixture(root);p.write_text('{"facts":{}}')
            self.assertIn('invalid submissions structure',inventory(root)['issues'][0])

# Execute selected real functions from the legacy script without its top-level
# downloads/writes. These characterize existing behavior, not full pipeline correctness.
def legacy_function(name, namespace):
    tree=ast.parse((ROOT/'scripts/step4_filters.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<legacy function>','exec'),namespace)
    return namespace[name]

class FilterCharacterizationTests(unittest.TestCase):
    def test_corrected_date_priority(self):
        fn=legacy_function('event_date',{'pd':pd})
        self.assertEqual(fn({'corrected_event_date':'2020-01-02','earliest_report_date':'2020-01-01'}),pd.Timestamp('2020-01-02'))
    def test_invalid_correction_not_silently_replaced(self):
        fn=legacy_function('event_date',{'pd':pd})
        self.assertTrue(pd.isna(fn({'corrected_event_date':'bad','earliest_report_date':'2020-01-01'})))
    def test_blank_correction_fallback(self):
        fn=legacy_function('event_date',{'pd':pd})
        self.assertEqual(fn({'corrected_event_date':'','earliest_report_date':'2020-01-01'}),pd.Timestamp('2020-01-01'))
    def test_price_calendar_drops_missing(self):
        px=pd.DataFrame({'ABC':[1,None,3]},index=pd.date_range('2020-01-01',periods=3))
        fn=legacy_function('trading_index',{'priced':{'ABC'},'px':px})
        self.assertEqual(len(fn('ABC')),2);self.assertIsNone(fn('MISSING'))

if __name__=='__main__': unittest.main()
