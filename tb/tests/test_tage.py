import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.tage import TAGEPredictor

class TAGEPredictorTest(unittest.TestCase):
    def test_basic_predict_update(self):
        tage = TAGEPredictor(tables=2, entries=16)
        pc = 0x100
        self.assertFalse(tage.predict(pc))
        for _ in range(3):
            tage.update(pc, True)
        self.assertTrue(tage.predict(pc))
        for _ in range(3):
            tage.update(pc, False)
        self.assertFalse(tage.predict(pc))

    def test_coverage(self):
        from tb.uvm_components.coverage import CoverageModel
        cov = CoverageModel()
        tage = TAGEPredictor(tables=2, entries=8, coverage=cov)
        tage.update(0x80, True)
        summary = cov.summary()
        self.assertEqual(summary["tage_entries"].get(0, 0), 1)

if __name__ == '__main__':
    unittest.main()
