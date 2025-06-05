import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rename.rename_unit import RenameUnit

class RenameUnitTest(unittest.TestCase):
    def test_basic_alloc_free(self):
        ru = RenameUnit()
        insts = [
            {"valid": True, "rs1": 1, "rs2": 2, "rd": 3},
            {"valid": True, "rs1": 4, "rs2": 5, "rd": 6},
        ]
        res = ru.allocate(insts)
        self.assertEqual(res[0]['rd_phys'], 32)
        self.assertEqual(res[0]['old_phys'], 3)
        self.assertEqual(res[1]['rd_phys'], 33)
        self.assertEqual(ru.free_count(), 94)  # 128-32-2
        ru.free(res[0]['rd_phys'])
        self.assertEqual(ru.free_count(), 95)

if __name__ == '__main__':
    unittest.main()
