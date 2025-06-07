import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.ex_units.vector_fma512 import VectorFMA512


class VectorFMA512Test(unittest.TestCase):
    def test_pipeline(self):
        fma = VectorFMA512()
        out_valid = False
        out = 0
        # feed one operation and then idle for a few cycles
        for cycle in range(7):
            if cycle == 0:
                valid = True
                a = 2
                b = 3
                c = 5
            else:
                valid = False
                a = b = c = 0
            out_valid, out = fma.step(valid, a, b, c)
            if cycle == 4:
                self.assertTrue(out_valid)
                self.assertEqual(out, (2 * 3 + 5) & ((1 << 512) - 1))

    def test_mask(self):
        fma = VectorFMA512()
        a = 0
        b = 0
        c = 0
        for lane in range(8):
            a |= (lane + 1) << (lane * 64)
            b |= (lane + 2) << (lane * 64)
            c |= (lane + 3) << (lane * 64)
        out = None
        for cycle in range(7):
            if cycle == 0:
                valid = True
                mask = 0x01  # update only lane 0
            else:
                valid = False
                mask = 0
            out_valid, out = fma.step(valid, a, b, c, mask)
            if cycle == 4:
                self.assertTrue(out_valid)
                lane0 = ((a & ((1 << 64) - 1)) * (b & ((1 << 64) - 1)) + (c & ((1 << 64) - 1))) & ((1 << 64) - 1)
                self.assertEqual(out & ((1 << 64) - 1), lane0)
                self.assertEqual(out >> 64, c >> 64)


if __name__ == "__main__":
    unittest.main()
