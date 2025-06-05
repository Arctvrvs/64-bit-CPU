import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tb.uvm_components.data_memory_model import DataMemoryModel

class DataMemoryModelTest(unittest.TestCase):
    def test_store_load(self):
        mem = DataMemoryModel()
        mem.store(0x100, 0x1122334455667788)
        self.assertEqual(mem.load(0x100), 0x1122334455667788 & 0xFFFFFFFFFFFFFFFF)
        mem.store(0x104, 0xAA55, size=2)
        self.assertEqual(mem.load(0x104, size=2), 0xAA55)

if __name__ == '__main__':
    unittest.main()
