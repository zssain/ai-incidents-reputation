import sys, unittest, tempfile, subprocess, math
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from step5_kappa import kappa, load
from output_safety import refuse_existing

class ValidationTests(unittest.TestCase):
    def test_undefined(self):
        self.assertTrue(math.isnan(kappa(["Y"]*3, ["Y"]*3)[0]))
    def test_empty(self):
        self.assertTrue(math.isnan(kappa([], [])[0]))
    def test_unequal(self):
        with self.assertRaises(ValueError): kappa([1], [])
    def test_perfect_nonconstant(self):
        self.assertEqual(kappa([1,2], [1,2]), (1,1))
    def test_observed(self):
        a=load(str(ROOT/"validation_astra.csv")); b=load(str(ROOT/"validation_coderB_human.csv"))
        m=a.merge(b,on="_key",suffixes=("_a","_b"),validate="one_to_one")
        self.assertEqual(len(m),30)
        k,po=kappa(m.responsibility_type_a.tolist(),m.responsibility_type_b.tolist())
        self.assertAlmostEqual(k,-1/24); self.assertAlmostEqual(po,25/30)
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"a.csv"
            f.write_text("incident_id,ticker,responsibility_type,correct_ticker,keep\n1,A,1,Y,Y\n1,A,1,Y,Y\n")
            with self.assertRaises(ValueError): load(str(f))
    def test_invalid_label(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"a.csv"
            f.write_text("incident_id,ticker,responsibility_type,correct_ticker,keep\n1,A,4,Y,Y\n")
            with self.assertRaises(ValueError): load(str(f))
    def test_protect_outputs(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"coder.xlsx"; f.write_bytes(b"original")
            with self.assertRaises(FileExistsError): refuse_existing([f])
            self.assertEqual(f.read_bytes(),b"original")
    def test_cli_and_rerun(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/"report"
            cmd=[sys.executable,str(ROOT/"scripts/step5_kappa.py"),str(ROOT/"validation_astra.csv"),str(ROOT/"validation_coderB_human.csv"),"--output-dir",str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
            before=(out/"metrics.csv").read_bytes()
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual((out/"metrics.csv").read_bytes(),before)
            self.assertEqual(len(pd.read_csv(out/"disagreements.csv")),9)
    def test_screening_preflight(self):
        import shutil
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/"scripts").mkdir()
            for name in ["step3_screening.py", "output_safety.py"]:
                shutil.copy(ROOT/"scripts"/name,root/"scripts"/name)
            f=root/"screening_coder_A.xlsx";f.write_bytes(b"original")
            r=subprocess.run([sys.executable,str(root/"scripts/step3_screening.py")],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("Refusing to overwrite",r.stderr)
            self.assertEqual(f.read_bytes(),b"original")

if __name__ == "__main__": unittest.main()
