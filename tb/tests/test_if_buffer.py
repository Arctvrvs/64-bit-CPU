import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.fetch.if_buffer import IFBuffer16


class IFBuffer16Test(unittest.TestCase):
    def test_fifo(self):
        buf = IFBuffer16()
        for i in range(16):
            self.assertTrue(buf.enqueue(i))
        self.assertFalse(buf.enqueue(99))
        for i in range(16):
            self.assertEqual(buf.dequeue(), i)
        self.assertIsNone(buf.dequeue())


if __name__ == "__main__":
    unittest.main()
