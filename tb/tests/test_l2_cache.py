import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.cache.l2_cache import L2Cache
from tb.uvm_components.coverage import CoverageModel

class L2CacheTest(unittest.TestCase):
    def test_read_write(self):
        cov = CoverageModel()
        c = L2Cache(coverage=cov)
        c.write(0x100, 42)
        self.assertEqual(c.read(0x100), 42)
        self.assertEqual(c.read(0x200), 0)
        summary = cov.summary()
        self.assertEqual(summary['cache_hits']['L2'], 1)
        self.assertEqual(summary['cache_misses']['L2'], 2)

if __name__ == '__main__':
    unittest.main()
