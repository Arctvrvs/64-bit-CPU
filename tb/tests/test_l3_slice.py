import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.interconnect.l3_slice_4m_8w import L3Slice

class L3SliceTest(unittest.TestCase):
    def test_read_write(self):
        s = L3Slice()
        s.write(0x10, 123)
        self.assertEqual(s.read(0x10), 123)
        self.assertEqual(s.read(0x20), 0)

if __name__ == '__main__':
    unittest.main()
