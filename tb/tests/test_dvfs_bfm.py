import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components.dvfs_bfm import DVFSBFM

class DVFSBFMTest(unittest.TestCase):
    def test_clock_toggle(self):
        bfm = DVFSBFM(period=2)
        seq = []
        for _ in range(6):
            seq.append(bfm.tick())
        self.assertEqual(seq, [0,1,1,0,0,1])
        bfm.set_period(3)
        seq2 = [bfm.tick() for _ in range(6)]
        self.assertEqual(seq2, [1,1,0,0,0,1])

if __name__ == '__main__':
    unittest.main()
