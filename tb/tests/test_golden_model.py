import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.isa.golden_model import GoldenModel


def encode_branch(funct3, rs1, rs2, imm):
    imm &= 0x1FFF
    return (
        ((imm >> 12) & 1) << 31
        | ((imm >> 5) & 0x3F) << 25
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (funct3 & 7) << 12
        | ((imm >> 1) & 0xF) << 8
        | ((imm >> 11) & 1) << 7
        | 0x63
    )


def encode_jal(rd, imm):
    imm &= 0x1FFFFF
    return (
        ((imm >> 20) & 1) << 31
        | ((imm >> 1) & 0x3FF) << 21
        | ((imm >> 11) & 1) << 20
        | ((imm >> 12) & 0xFF) << 12
        | (rd & 0x1F) << 7
        | 0x6F
    )


def encode_jalr(rd, rs1, imm):
    imm &= 0xFFF
    return (
        (imm & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | 0 << 12
        | (rd & 0x1F) << 7
        | 0x67
    )


def encode_lr(rd, rs1):
    return (
        (0x02 << 27)
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )


def encode_sc(rd, rs1, rs2):
    return (
        (0x03 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )


def encode_amoadd(rd, rs1, rs2):
    return (
        (0x00 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )


def encode_amoswap(rd, rs1, rs2):
    return (
        (0x01 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

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

    def test_mul_div_rem(self):
        gm = GoldenModel()
        gm.step(0x00A00093)  # addi x1,x0,10
        gm.step(0x00500113)  # addi x2,x0,5
        gm.step(0x022081b3)  # mul x3,x1,x2 -> 50
        gm.step(0x0211c233)  # div x4,x3,x1 -> 5
        gm.step(0x0221e2b3)  # rem x5,x3,x2 -> 0
        self.assertEqual(gm.regs[3], 50)
        self.assertEqual(gm.regs[4], 5)
        self.assertEqual(gm.regs[5], 0)


    def test_logic_and_shifts(self):
        gm = GoldenModel()
        gm.step(0x00100093)  # addi x1,x0,1
        gm.step(0x00409093)  # slli x1,x1,4 -> 16
        gm.step(0x0020d113)  # srli x2,x1,2 -> 4
        gm.step(0x4010d193)  # srai x3,x1,1 -> 8
        gm.step(0x00f0e213)  # ori x4,x1,0xf -> 0x1f
        gm.step(0x00f27293)  # andi x5,x4,0xf -> 0xf
        gm.step(0x0f02c313)  # xori x6,x5,0xf0 -> 0xff
        gm.step(0x123453b7)  # lui x7,0x12345
        gm.step(0x00abc417)  # auipc x8,0xabc
        self.assertEqual(gm.regs[1], 16)
        self.assertEqual(gm.regs[2], 4)
        self.assertEqual(gm.regs[3], 8)
        self.assertEqual(gm.regs[4], 0x1F)
        self.assertEqual(gm.regs[5], 0xF)
        self.assertEqual(gm.regs[6], 0xFF)
        self.assertEqual(gm.regs[7], 0x12345000)
        self.assertEqual(gm.regs[8], 0xABC020)

    def test_jal_and_jalr(self):
        gm = GoldenModel()
        gm.step(encode_jal(1, 8))  # jal x1,8
        self.assertEqual(gm.pc, 8)
        self.assertEqual(gm.regs[1], 4)
        gm.regs[5] = 100
        gm.step(encode_jalr(2, 5, 4))  # jalr x2,x5,4
        self.assertEqual(gm.pc, 104)
        self.assertEqual(gm.regs[2], 12)

    def test_blt_bge(self):
        gm = GoldenModel()
        gm.regs[1] = 5
        gm.regs[2] = 10
        gm.step(encode_branch(0x4, 1, 2, 4))  # blt x1,x2,4
        self.assertEqual(gm.pc, 4)
        gm.step(encode_branch(0x5, 2, 1, 4))  # bge x2,x1,4
        self.assertEqual(gm.pc, 8)

    def test_lr_sc_and_amo(self):
        gm = GoldenModel()
        gm.regs[2] = 0x100
        gm.load_memory(0x100, 5)
        gm.step(encode_lr(1, 2))  # lr.d x1,(x2)
        self.assertEqual(gm.regs[1], 5)
        gm.regs[3] = 7
        gm.step(encode_sc(4, 2, 3))  # sc.d x3,(x2)
        self.assertEqual(gm.regs[4], 0)
        self.assertEqual(gm.mem[0x100], 7)
        gm.regs[3] = 9
        gm.regs[2] = 0x108
        gm.step(encode_sc(4, 2, 3))  # sc.d should fail
        self.assertEqual(gm.regs[4], 1)
        gm.regs[2] = 0x100
        gm.step(encode_amoadd(5, 2, 3))  # amoadd.d x5,(x2),x3
        self.assertEqual(gm.regs[5], 7)
        self.assertEqual(gm.mem[0x100], 16)
        gm.step(encode_amoswap(6, 2, 3))  # amoswap.d x6,(x2),x3
        self.assertEqual(gm.regs[6], 16)
        self.assertEqual(gm.mem[0x100], 9)

if __name__ == '__main__':
    unittest.main()
