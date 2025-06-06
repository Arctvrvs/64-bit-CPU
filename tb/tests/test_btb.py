import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.btb import BTB
from tb.uvm_components.coverage import CoverageModel

class BTBTest(unittest.TestCase):
    def test_basic_predict_update(self):
        btb = BTB(entries=4)
        pc = 0x100
        taken, tgt = btb.predict(pc)
        self.assertFalse(taken)
        btb.update(pc, 0x200, True)
        taken, tgt = btb.predict(pc)
        self.assertTrue(taken)
        self.assertEqual(tgt, 0x200)
        # update not taken should keep entry but mark new target
        btb.update(pc, 0x104, False)
        taken, tgt = btb.predict(pc)
        self.assertTrue(taken)
        self.assertEqual(tgt, 0x104)

    def test_coverage_integration(self):
        cov = CoverageModel()
        btb = BTB(entries=8, coverage=cov)
        pc = 0x200
        btb.update(pc, 0x300, True)
        summary = cov.summary()
        self.assertEqual(summary["btb_entries"], 1)

if __name__ == '__main__':
    unittest.main()
