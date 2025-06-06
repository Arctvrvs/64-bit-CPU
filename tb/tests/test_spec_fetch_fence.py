import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.security.spec_fetch_fence import SpecFetchFence

class SpecFetchFenceTest(unittest.TestCase):
    def test_fence_allows_load(self):
        f = SpecFetchFence()
        self.assertTrue(f.allow_load())
        f.fence()
        self.assertFalse(f.allow_load())
        f.retire_branch()
        self.assertTrue(f.allow_load())

if __name__ == "__main__":
    unittest.main()
