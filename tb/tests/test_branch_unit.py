import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.ex_units.branch_unit import BranchUnit


class BranchUnitTest(unittest.TestCase):
    def test_taken_prediction(self):
        bu = BranchUnit()
        res = bu.compute(
            BranchUnit.BEQ, 5, 5, 0, 8,
            predicted_taken=True, predicted_target=8
        )
        self.assertTrue(res["taken"])
        self.assertEqual(res["target"], 8)
        self.assertFalse(res["mispredict"])

    def test_not_taken_mispredict(self):
        bu = BranchUnit()
        res = bu.compute(
            BranchUnit.BNE, 0, 0, 0, 8,
            predicted_taken=True, predicted_target=8
        )
        self.assertFalse(res["taken"])
        self.assertEqual(res["target"], 4)
        self.assertTrue(res["mispredict"])

    def test_jalr_alignment(self):
        bu = BranchUnit()
        res = bu.compute(BranchUnit.JALR, 2, 0, 0, 1)
        self.assertTrue(res["taken"])
        self.assertEqual(res["target"], (2 + 1) & 0xFFFFFFFFFFFFFFFE)


if __name__ == "__main__":
    unittest.main()
