import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l1_icache import L1ICache
from rtl.mmu import TlbL1, TlbL2, PageWalker8
from tb.uvm_components.coverage import CoverageModel


class L1ICacheTest(unittest.TestCase):
    def test_fetch(self):
        cov = CoverageModel()
        tlb1 = TlbL1(coverage=cov)
        tlb2 = TlbL2(coverage=cov)
        walker = PageWalker8()
        walker.set_entry(0x1000, 0x80001000, perm='x')
        c = L1ICache(tlb_l1=tlb1, tlb_l2=tlb2, walker=walker, coverage=cov)
        c.load(0x80001000, 0xDEADBEEF)
        self.assertEqual(c.fetch(0x1000), 0xDEADBEEF)
        self.assertEqual(c.fetch(0x2000), 0)
        summary = cov.summary()
        self.assertEqual(summary['cache_hits']['L1'], 1)
        self.assertEqual(summary['cache_misses']['L1'], 1)

    def test_fault(self):
        cov = CoverageModel()
        c = L1ICache(coverage=cov)
        self.assertEqual(c.fetch(0x3000), 0)
        self.assertEqual(cov.summary()['cache_misses']['L1'], 1)


if __name__ == "__main__":
    unittest.main()
