import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.interconnect.l3_cache_16m_8w import L3Cache16M8W
from tb.uvm_components.coverage import CoverageModel

class L3Cache16M8WTest(unittest.TestCase):
    def test_read_write(self):
        cov = CoverageModel()
        cache = L3Cache16M8W(coverage=cov)
        cache.write(0x40, 42)
        self.assertEqual(cache.read(0x40), 42)
        self.assertEqual(cache.read(0x80), 0)
        summary = cov.summary()
        self.assertEqual(summary['cache_hits']['L3'], 1)
        self.assertEqual(summary['cache_misses']['L3'], 2)

if __name__ == '__main__':
    unittest.main()
