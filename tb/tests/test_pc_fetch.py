import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.fetch.pc_fetch import PCFetch


class PCFetchTest(unittest.TestCase):
    def test_pc_sequence(self):
        pc = PCFetch(reset_vector=0)
        self.assertEqual(pc.pc_if2(), 0)
        pc.step()
        self.assertEqual(pc.pc_if2(), 8)
        pc.step(branch_taken=True, branch_target=0x40)
        self.assertEqual(pc.pc_if2(), 0x40)
        self.assertEqual(pc.pc_if1_plus8(), 0x48)


if __name__ == "__main__":
    unittest.main()
