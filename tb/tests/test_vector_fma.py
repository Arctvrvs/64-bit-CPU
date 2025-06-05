import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.ex_units.vector_fma import VectorFMA

class VectorFMATest(unittest.TestCase):
    def test_execute(self):
        v = VectorFMA()
        a = list(range(8))
        b = [2]*8
        c = [1]*8
        res = v.execute(a, b, c)
        self.assertEqual(res[0], 1)
        self.assertEqual(res[7], 2*7 + 1)

if __name__ == '__main__':
    unittest.main()
