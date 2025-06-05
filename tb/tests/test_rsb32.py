import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.rsb32 import ReturnStackBuffer


class RSBTest(unittest.TestCase):
    def test_push_pop(self):
        rsb = ReturnStackBuffer(depth=4)
        rsb.push(0x100)
        rsb.push(0x200)
        rsb.push(0x300)
        self.assertEqual(rsb.top(), 0x300)
        self.assertEqual(rsb.pop(), 0x300)
        self.assertEqual(rsb.pop(), 0x200)
        rsb.push(0x400)
        rsb.push(0x500)
        # stack should wrap around
        self.assertEqual(rsb.pop(), 0x500)
        self.assertEqual(rsb.pop(), 0x400)
        self.assertEqual(rsb.pop(), 0x100)


if __name__ == "__main__":
    unittest.main()
