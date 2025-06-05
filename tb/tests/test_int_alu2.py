import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.ex_units.int_alu2 import IntALU2

class IntALU2Test(unittest.TestCase):
    def test_dual_ops(self):
        alu = IntALU2()
        results = alu.cycle([
            {"op1": 5, "op2": 3, "alu_ctrl": IntALU2.ALU_ADD, "dest": 1, "rob": 0},
            {"op1": 7, "op2": 2, "alu_ctrl": IntALU2.ALU_SUB, "dest": 2, "rob": 1},
        ])
        self.assertEqual(results[0]["result"], 8)
        self.assertEqual(results[1]["result"], 5)
        self.assertEqual(results[0]["dest"], 1)
        self.assertEqual(results[1]["rob"], 1)

    def test_shifts_and_logic(self):
        alu = IntALU2()
        results = alu.cycle([
            {"op1": 1, "op2": 3, "alu_ctrl": IntALU2.ALU_SLL},
            {"op1": 0xF0F0, "op2": 0x0FF0, "alu_ctrl": IntALU2.ALU_AND},
        ])
        self.assertEqual(results[0]["result"], 8)
        self.assertEqual(results[1]["result"], 0xF0F0 & 0x0FF0)

if __name__ == "__main__":
    unittest.main()
