import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.csr.csr_file import CsrFile

class CsrFileTest(unittest.TestCase):
    def test_read_write_and_counters(self):
        csr = CsrFile()
        self.assertEqual(csr.read(5), 0)
        csr.write(5, 123)
        self.assertEqual(csr.read(5), 123)
        csr.step(instret_inc=1)
        csr.step(instret_inc=2)
        self.assertEqual(csr.read(0xC00), 2)
        self.assertEqual(csr.read(0xC02), 3)

if __name__ == '__main__':
    unittest.main()
