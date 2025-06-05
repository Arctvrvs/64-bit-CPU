import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.interconnect.l3_cache_16m_8w import L3Cache16M8W

class L3Cache16M8WTest(unittest.TestCase):
    def test_read_write(self):
        cache = L3Cache16M8W()
        cache.write(0x40, 42)
        self.assertEqual(cache.read(0x40), 42)
        self.assertEqual(cache.read(0x80), 0)

if __name__ == '__main__':
    unittest.main()
