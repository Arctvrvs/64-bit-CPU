import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tb.uvm_components.regfile_bfm import RegFileBFM

class RegFileBFMTest(unittest.TestCase):
    def test_simple_writes(self):
        bfm = RegFileBFM()
        # addi x1,x0,5
        self.assertTrue(bfm.write(0x00500093, 1, 5))
        # add x2,x1,x1 -> should be 10
        self.assertTrue(bfm.write(0x00108133, 2, 10))
        # mismatch should return False
        self.assertFalse(bfm.write(0x001101b3, 3, 1))

if __name__ == "__main__":
    unittest.main()
