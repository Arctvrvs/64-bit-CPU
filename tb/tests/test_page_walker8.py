import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.mmu.page_walker8 import PageWalker8
from tb.uvm_components.coverage import CoverageModel

class PageWalker8Test(unittest.TestCase):
    def test_walk(self):
        cov = CoverageModel()
        pw = PageWalker8(coverage=cov)
        va = 0x1000
        pw.set_entry(va, 0x80001000, perm='rwx')
        pa, fault = pw.walk(va, perm='r')
        self.assertEqual(pa, 0x80001000)
        self.assertFalse(fault)
        pa, fault = pw.walk(va, perm='w')
        self.assertFalse(fault)
        miss_pa, miss_fault = pw.walk(0x2000)
        self.assertTrue(miss_fault)
        summary = cov.summary()
        self.assertEqual(summary["page_walks"], 3)
        self.assertEqual(summary["page_walk_faults"], 1)

if __name__ == '__main__':
    unittest.main()
