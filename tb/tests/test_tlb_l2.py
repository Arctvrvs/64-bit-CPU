import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.mmu.tlb_l2 import TlbL2

class TlbL2Test(unittest.TestCase):
    def test_lookup(self):
        tlb = TlbL2(entries=2)
        va = 0x1000
        hit, pa, fault = tlb.lookup(va)
        self.assertFalse(hit)
        tlb.refill(va, 0x80001000, perm='rw')
        hit, pa, fault = tlb.lookup(va, perm='r')
        self.assertTrue(hit)
        self.assertEqual(pa, 0x80001000)
        self.assertFalse(fault)
        hit, pa, fault = tlb.lookup(va, perm='x')
        self.assertTrue(fault)

if __name__ == '__main__':
    unittest.main()
