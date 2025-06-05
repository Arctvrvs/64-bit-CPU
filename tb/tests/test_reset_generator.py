import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components.reset_generator import ResetGenerator

class ResetGeneratorTest(unittest.TestCase):
    def test_pulse(self):
        rg = ResetGenerator(cycles=2)
        self.assertEqual(rg.get(), 0)
        self.assertEqual(rg.tick(), 0)
        self.assertEqual(rg.tick(), 1)
        self.assertEqual(rg.get(), 1)
        rg.reset()
        self.assertEqual(rg.get(), 0)

if __name__ == '__main__':
    unittest.main()
