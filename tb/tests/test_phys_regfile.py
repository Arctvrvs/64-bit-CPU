import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rf.phys_regfile import PhysRegFile

class PhysRegFileTest(unittest.TestCase):
    def test_multiport_write_read(self):
        prf = PhysRegFile()
        for idx in range(0, 128, 17):
            prf.write(idx, idx + 0x100)
        for idx in range(0, 128, 17):
            self.assertEqual(prf.read(idx), idx + 0x100)

if __name__ == "__main__":
    unittest.main()
