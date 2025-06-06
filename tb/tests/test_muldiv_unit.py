import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.ex_units.muldiv_unit import MulDivUnit

class MulDivUnitTest(unittest.TestCase):
    def test_mul_and_div(self):
        md = MulDivUnit(mul_latency=2, div_latency=3)
        # cycle 0 issue both
        res = md.cycle(mul_op={"op_a": 2, "op_b": 3, "dest": 1, "rob": 0},
                        div_op={"dividend": 9, "divisor": 3, "dest": 2, "rob": 1})
        self.assertEqual(res, (None, None))
        # cycle 1
        mul_res, div_res = md.cycle()
        # mul result available after two cycles
        self.assertIsNotNone(mul_res)
        self.assertEqual(mul_res["result"], 6)
        self.assertIsNone(div_res)
        # cycle 2 -> div result
        mul_res, div_res = md.cycle()
        self.assertIsNone(mul_res)
        self.assertIsNotNone(div_res)
        self.assertEqual(div_res["result"], 3)

if __name__ == "__main__":
    unittest.main()
