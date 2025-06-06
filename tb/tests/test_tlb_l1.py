import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.mmu.tlb_l1 import TlbL1
from tb.uvm_components.coverage import CoverageModel

class TlbL1Test(unittest.TestCase):
    def test_lookup_and_refill(self):
        cov = CoverageModel()
        tlb = TlbL1(entries=2, coverage=cov)
        va = 0x1000
        hit, pa, fault = tlb.lookup(va)
        self.assertFalse(hit)
        self.assertFalse(fault)
        self.assertEqual(cov.summary()['tlb_misses']['L1'], 1)
        self.assertEqual(cov.summary()['tlb_latency']['L1'], [5])

        tlb.refill(va, 0x80001000, perm='rw')
        hit, pa, fault = tlb.lookup(va, perm='r')
        self.assertTrue(hit)
        self.assertEqual(pa, 0x80001000)
        self.assertFalse(fault)
        self.assertEqual(cov.summary()['tlb_hits']['L1'], 1)
        self.assertEqual(cov.summary()['tlb_latency']['L1'][-1], 1)

        hit, pa, fault = tlb.lookup(va, perm='x')
        self.assertTrue(hit)
        self.assertTrue(fault)
        self.assertEqual(cov.summary()['tlb_faults']['L1'], 1)
