import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.mmu.page_walker import PageWalker
from tb.uvm_components.coverage import CoverageModel

class PageWalkerTest(unittest.TestCase):
    def test_walk(self):
        cov = CoverageModel()
        pw = PageWalker(coverage=cov)
        va = 0x2000
        pw.set_entry(va, 0x80002000, perm='r')
        pa, fault = pw.walk(va, perm='r')
        self.assertEqual(pa, 0x80002000)
        self.assertFalse(fault)
        pa, fault = pw.walk(va, perm='w')
        self.assertTrue(fault)
        miss_pa, miss_fault = pw.walk(0x3000)
        self.assertTrue(miss_fault)
        summary = cov.summary()
        self.assertEqual(summary["page_walks"], 3)
        self.assertEqual(summary["page_walk_faults"], 2)

if __name__ == '__main__':
    unittest.main()
