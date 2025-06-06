import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.lsu.lsu import LSU
from rtl.mmu import TlbL1, TlbL2, PageWalker8

class LsuTest(unittest.TestCase):
    def test_load_store(self):
        tlb1 = TlbL1()
        tlb2 = TlbL2()
        walker = PageWalker8()
        walker.set_entry(0x1000, 0x80001000, perm='rw')
        lsu = LSU(tlb_l1=tlb1, tlb_l2=tlb2, walker=walker)
        # store 64-bit value
        lsu.cycle([
            {"is_store": True, "addr": 0x1000, "data": 0x1122334455667788, "size": 8},
            None,
        ])
        # load back
        res = lsu.cycle([
            {"is_store": False, "addr": 0x1000, "size": 8, "dest": 5, "rob": 1},
            None,
        ])
        self.assertEqual(res[0]["data"], 0x1122334455667788)
        self.assertEqual(res[0]["dest"], 5)
        self.assertEqual(res[0]["rob"], 1)

    def test_fault(self):
        tlb1 = TlbL1()
        tlb2 = TlbL2()
        walker = PageWalker8()
        walker.set_entry(0x2000, 0x80002000, perm='r')
        lsu = LSU(tlb_l1=tlb1, tlb_l2=tlb2, walker=walker)
        res = lsu.cycle([
            {"is_store": True, "addr": 0x2000, "data": 1, "size": 8, "rob": 3},
            None,
        ])
        self.assertTrue(res[0]["fault"])
        self.assertEqual(res[0]["rob"], 3)

if __name__ == "__main__":
    unittest.main()
