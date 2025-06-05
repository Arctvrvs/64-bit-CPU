import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l1_dcache import L1DCache


class L1DCacheTest(unittest.TestCase):
    def test_read_write_with_strobe(self):
        c = L1DCache()
        c.write(0x100, 0x1122334455667788)
        self.assertEqual(c.read(0x100), 0x1122334455667788)
        c.write(0x100, 0x00000000000000FF, wstrb=0x01)
        self.assertEqual(c.read(0x100), 0x11223344556677FF)
        c.write(0x100, 0xAA00000000000000, wstrb=0x80)
        self.assertEqual(c.read(0x100), 0xAA223344556677FF)


if __name__ == "__main__":
    unittest.main()
