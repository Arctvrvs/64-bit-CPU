import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from rtl.ex_units.amo_unit import AmoUnit


class AmoUnitTest(unittest.TestCase):
    def test_add_and_swap(self):
        au = AmoUnit()
        res_add = au.compute(1, 2, AmoUnit.AMO_ADD)
        self.assertEqual(res_add, 3)
        res_swap = au.compute(5, 9, AmoUnit.AMO_SWAP)
        self.assertEqual(res_swap, 9)


if __name__ == "__main__":
    unittest.main()
