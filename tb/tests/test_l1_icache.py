import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l1_icache import L1ICache
from rtl.mmu import TlbL1, TlbL2, PageWalker8


class L1ICacheTest(unittest.TestCase):
    def test_fetch(self):
        tlb1 = TlbL1()
        tlb2 = TlbL2()
        walker = PageWalker8()
        walker.set_entry(0x1000, 0x80001000, perm='x')
        c = L1ICache(tlb_l1=tlb1, tlb_l2=tlb2, walker=walker)
        c.load(0x80001000, 0xDEADBEEF)
        self.assertEqual(c.fetch(0x1000), 0xDEADBEEF)
        self.assertEqual(c.fetch(0x2000), 0)

    def test_fault(self):
        c = L1ICache()
        self.assertEqual(c.fetch(0x3000), 0)


if __name__ == "__main__":
    unittest.main()
