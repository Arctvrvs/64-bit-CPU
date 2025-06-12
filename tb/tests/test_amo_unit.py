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

    def test_other_ops(self):
        au = AmoUnit()
        self.assertEqual(au.compute(0xF0, 0x0F, AmoUnit.AMO_XOR), 0xFF)
        self.assertEqual(au.compute(0xF0, 0x0F, AmoUnit.AMO_OR), 0xFF)
        self.assertEqual(au.compute(0xF0, 0x0F, AmoUnit.AMO_AND), 0x00)
        self.assertEqual(au.compute(5, 10, AmoUnit.AMO_MIN), 5)
        self.assertEqual(au.compute(5, 10, AmoUnit.AMO_MAX), 10)
        self.assertEqual(au.compute(5, 10, AmoUnit.AMO_MINU), 5)
        self.assertEqual(au.compute(5, 10, AmoUnit.AMO_MAXU), 10)


if __name__ == "__main__":
    unittest.main()
