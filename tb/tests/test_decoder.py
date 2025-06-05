import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.decode.decoder8w import Decoder8W

class Decoder8WTest(unittest.TestCase):
    def test_simple_decode(self):
        dec = Decoder8W()
        instrs = [
            0x00b50533,  # add x10,x10,x11
            0x00128293,  # addi x5,x5,1
            0x00b52023,  # sw x11,0(x10)
            0x00b50663,  # beq x10,x11,12
        ]
        res = dec.decode(instrs)
        self.assertEqual(res[0]['rd'], 10)
        self.assertEqual(res[0]['rs1'], 10)
        self.assertEqual(res[0]['rs2'], 11)
        self.assertFalse(res[0]['is_branch'])
        self.assertEqual(res[1]['imm'], 1)
        self.assertTrue(res[2]['is_store'])
        self.assertTrue(res[3]['is_branch'])

if __name__ == '__main__':
    unittest.main()
