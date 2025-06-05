import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.branch_predictor import BranchPredictor

class BranchPredictorTest(unittest.TestCase):
    def test_basic_prediction(self):
        bp = BranchPredictor(entries=8)
        pc = 0x100
        taken, target = bp.predict(pc)
        self.assertFalse(taken)
        self.assertEqual(target, pc + 4)
        # Train taken branch
        bp.update(pc, True, 0x200)
        taken, target = bp.predict(pc)
        self.assertTrue(taken)
        self.assertEqual(target, 0x200)
        # Train not taken twice to flip prediction
        bp.update(pc, False, 0x104)
        bp.update(pc, False, 0x104)
        taken, target = bp.predict(pc)
        self.assertFalse(taken)
        self.assertEqual(target, 0x104)

if __name__ == '__main__':
    unittest.main()
