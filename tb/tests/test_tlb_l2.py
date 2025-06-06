import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.mmu.tlb_l2 import TlbL2
from tb.uvm_components.coverage import CoverageModel

class TlbL2Test(unittest.TestCase):
    def test_lookup(self):
        cov = CoverageModel()
        tlb = TlbL2(entries=2, coverage=cov)
        va = 0x1000
        hit, pa, fault = tlb.lookup(va)
        self.assertFalse(hit)
        self.assertEqual(cov.summary()['tlb_misses']['L2'], 1)
        self.assertEqual(cov.summary()['tlb_latency']['L2'], [20])

        tlb.refill(va, 0x80001000, perm='rw')
        hit, pa, fault = tlb.lookup(va, perm='r')
        self.assertTrue(hit)
        self.assertEqual(pa, 0x80001000)
        self.assertFalse(fault)
        self.assertEqual(cov.summary()['tlb_hits']['L2'], 1)
        self.assertEqual(cov.summary()['tlb_latency']['L2'][-1], 8)

        hit, pa, fault = tlb.lookup(va, perm='x')
        self.assertTrue(fault)
        self.assertEqual(cov.summary()['tlb_faults']['L2'], 1)

if __name__ == '__main__':
    unittest.main()
