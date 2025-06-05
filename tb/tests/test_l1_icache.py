import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l1_icache import L1ICache


class L1ICacheTest(unittest.TestCase):
    def test_fetch(self):
        c = L1ICache()
        c.load(0x1000, 0xDEADBEEF)
        self.assertEqual(c.fetch(0x1000), 0xDEADBEEF)
        self.assertEqual(c.fetch(0x2000), 0)


if __name__ == "__main__":
    unittest.main()
