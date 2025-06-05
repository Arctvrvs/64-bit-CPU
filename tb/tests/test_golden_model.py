import unittest
from rtl.isa.golden_model import GoldenModel

class GoldenModelTest(unittest.TestCase):
    def test_add_and_addi(self):
        gm = GoldenModel()
        gm.step(0x00500093)  # addi x1,x0,5
        gm.step(0x00300113)  # addi x2,x0,3
        gm.step(0x002081b3)  # add x3,x1,x2
        self.assertEqual(gm.regs[1], 5)
        self.assertEqual(gm.regs[2], 3)
        self.assertEqual(gm.regs[3], 8)
        self.assertEqual(gm.pc, 12)

    def test_branch(self):
        gm = GoldenModel()
        gm.step(0x00500093)  # addi x1,x0,5
        gm.step(0x00008463)  # beq x1,x0,8 (not taken)
        self.assertEqual(gm.pc, 8)
        gm.step(0x00008063)  # beq x1,x0,0 (taken if x1==x0) -> not taken
        self.assertEqual(gm.pc, 12)
        gm.step(0x00000463)  # beq x0,x0,8 -> taken
        self.assertEqual(gm.pc, 20)

if __name__ == '__main__':
    unittest.main()
