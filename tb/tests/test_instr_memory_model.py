import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components.instr_memory_model import InstructionMemoryModel

class InstrMemoryModelTest(unittest.TestCase):
    def test_load_and_fetch(self):
        imem = InstructionMemoryModel()
        imem.load_program(0x1000, [0xDEADBEEF, 0x12345678])
        self.assertEqual(imem.fetch(0x1000), 0xDEADBEEF & 0xFFFFFFFF)
        self.assertEqual(imem.fetch(0x1004), 0x12345678)
        self.assertEqual(imem.fetch(0x2000), 0)

if __name__ == '__main__':
    unittest.main()
