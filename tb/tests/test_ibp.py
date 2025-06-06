import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.ibp import IBPPredictor

class IBPPredictorTest(unittest.TestCase):
    def test_basic_predict_update(self):
        ibp = IBPPredictor(entries=8)
        pc = 0x80
        last = 0x20
        self.assertEqual(ibp.predict(pc, last), 0)
        ibp.update(pc, last, 0x1234)
        self.assertEqual(ibp.predict(pc, last), 0x1234)
        # Different last target should not hit
        self.assertEqual(ibp.predict(pc, last + 4), 0)

    def test_coverage(self):
        from tb.uvm_components.coverage import CoverageModel
        cov = CoverageModel()
        ibp = IBPPredictor(entries=4, coverage=cov)
        ibp.update(0x40, 0x10, 0x44)
        summary = cov.summary()
        self.assertEqual(summary["ibp_entries"], 1)

if __name__ == '__main__':
    unittest.main()
