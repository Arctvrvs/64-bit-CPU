import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.decode.decoder8w import Decoder8W
from tb.uvm_components.coverage import CoverageModel

class Decoder8WTest(unittest.TestCase):
    def test_simple_decode(self):
        dec = Decoder8W()
        instrs = [
            0x00b50533,  # add x10,x10,x11
            0x00128293,  # addi x5,x5,1
            0x00b52023,  # sw x11,0(x10)
            0x00b50663,  # beq x10,x11,12
            0x00003103,  # ld x2,0(x0)
        ]
        res = dec.decode(instrs)
        self.assertEqual(res[0]['rd'], 10)
        self.assertEqual(res[0]['rs1'], 10)
        self.assertEqual(res[0]['rs2'], 11)
        self.assertFalse(res[0]['is_branch'])
        self.assertEqual(res[1]['imm'], 1)
        self.assertTrue(res[2]['is_store'])
        self.assertTrue(res[3]['is_branch'])
        self.assertEqual(res[3]['imm'], 12)
        self.assertTrue(res[4]['is_load'])

    def test_coverage_hook(self):
        cov = CoverageModel()
        dec = Decoder8W()
        instrs = [0x00128293, 0x00b50663]
        dec.decode(instrs, coverage=cov)
        summary = cov.summary()
        self.assertEqual(summary['opcodes'], 2)
        self.assertEqual(summary['immediates'], 2)

if __name__ == '__main__':
    unittest.main()
