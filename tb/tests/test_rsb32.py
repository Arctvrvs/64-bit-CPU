import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.rsb32 import ReturnStackBuffer
from tb.uvm_components.coverage import CoverageModel


class RSBTest(unittest.TestCase):
    def test_push_pop(self):
        rsb = ReturnStackBuffer(depth=4)
        rsb.push(0x100)
        rsb.push(0x200)
        rsb.push(0x300)
        self.assertEqual(rsb.top(), 0x300)
        self.assertEqual(rsb.pop(), 0x300)
        self.assertEqual(rsb.pop(), 0x200)
        rsb.push(0x400)
        rsb.push(0x500)
        # stack should wrap around
        self.assertEqual(rsb.pop(), 0x500)
        self.assertEqual(rsb.pop(), 0x400)
        self.assertEqual(rsb.pop(), 0x100)

    def test_coverage_under_overflow(self):
        cov = CoverageModel()
        rsb = ReturnStackBuffer(depth=2, coverage=cov)
        rsb.push(0x1)
        rsb.push(0x2)
        rsb.push(0x3)  # overflow
        rsb.pop()
        rsb.pop()
        rsb.pop()  # underflow
        summary = cov.summary()
        self.assertEqual(summary["rsb_overflow"], 1)
        self.assertEqual(summary["rsb_underflow"], 1)


if __name__ == "__main__":
    unittest.main()
