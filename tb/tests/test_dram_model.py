import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.interconnect.dram_model import DRAMModel

class DRAMModelTest(unittest.TestCase):
    def test_read_write(self):
        d = DRAMModel()
        d.write(0x40, 99)
        self.assertEqual(d.read(0x40), 99)
        self.assertEqual(d.read(0x50), 0)

if __name__ == '__main__':
    unittest.main()
