import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l2_cache import L2Cache

class L2CacheTest(unittest.TestCase):
    def test_read_write(self):
        c = L2Cache()
        c.write(0x100, 42)
        self.assertEqual(c.read(0x100), 42)
        self.assertEqual(c.read(0x200), 0)

if __name__ == '__main__':
    unittest.main()
