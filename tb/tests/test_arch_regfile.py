import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rf.arch_regfile import ArchRegFile

class ArchRegFileTest(unittest.TestCase):
    def test_write_and_read(self):
        arf = ArchRegFile()
        for i in range(1, 32):
            arf.write(i, i * 3)
        for i in range(1, 32):
            self.assertEqual(arf.read(i), i * 3)
        arf.write(0, 123)
        self.assertEqual(arf.read(0), 0)

if __name__ == "__main__":
    unittest.main()
