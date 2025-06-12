import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.isa.golden_model import GoldenModel
from tb.uvm_components.coverage import CoverageModel


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

def encode_amoxor(rd, rs1, rs2):
    return (
        (0x04 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amoor(rd, rs1, rs2):
    return (
        (0x08 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amoand(rd, rs1, rs2):
    return (
        (0x0C << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amomin(rd, rs1, rs2):
    return (
        (0x10 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amomax(rd, rs1, rs2):
    return (
        (0x14 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amominu(rd, rs1, rs2):
    return (
        (0x18 << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_amomaxu(rd, rs1, rs2):
    return (
        (0x1C << 27)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x3 << 12)
        | (rd & 0x1F) << 7
        | 0x2F
    )

def encode_addw(rd, rs1, rs2):
    return (
        (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x0 << 12)
        | (rd & 0x1F) << 7
        | 0x3B
    )

def encode_subw(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x0 << 12)
        | (rd & 0x1F) << 7
        | 0x3B
    )

def encode_sllw(rd, rs1, rs2):
    return (
        (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x1 << 12)
        | (rd & 0x1F) << 7
        | 0x3B
    )

def encode_srlw(rd, rs1, rs2):
    return (
        (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x3B
    )

def encode_sraw(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x3B
    )

def encode_addiw(rd, rs1, imm):
    imm &= 0xFFF
    return (
        (imm & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (0x0 << 12)
        | (rd & 0x1F) << 7
        | 0x1B
    )

def encode_slliw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x00 << 25)
        | (shamt & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x1 << 12)
        | (rd & 0x1F) << 7
        | 0x1B
    )

def encode_srliw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x00 << 25)
        | (shamt & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x1B
    )

def encode_sraiw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x20 << 25)
        | (shamt & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x1B
    )

def encode_spec_fence():
    return 0x0000200F

def encode_faddd(rd, rs1, rs2, rm=0):
    return (
        (0x01 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fsubd(rd, rs1, rs2, rm=0):
    return (
        (0x05 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fmuld(rd, rs1, rs2, rm=0):
    return (
        (0x09 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fdivd(rd, rs1, rs2, rm=0):
    return (
        (0x0D << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fmind(rd, rs1, rs2, rm=0):
    return (
        (0x15 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fmaxd(rd, rs1, rs2, rm=1):
    return (
        (0x15 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x53
    )


def encode_fmaddd(rd, rs1, rs2, rs3, rm=0):
    return (
        (rs3 & 0x1F) << 27
        | (0x1 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x43
    )


def encode_fmsubd(rd, rs1, rs2, rs3, rm=0):
    return (
        (rs3 & 0x1F) << 27
        | (0x1 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x47
    )


def encode_fnmsubd(rd, rs1, rs2, rs3, rm=0):
    return (
        (rs3 & 0x1F) << 27
        | (0x1 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x4B
    )


def encode_fnmaddd(rd, rs1, rs2, rs3, rm=0):
    return (
        (rs3 & 0x1F) << 27
        | (0x1 << 25)
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (rm & 7) << 12
        | (rd & 0x1F) << 7
        | 0x4F
    )


def encode_load(funct3, rd, rs1, imm):
    imm &= 0xFFF
    return (
        (imm & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (funct3 & 7) << 12
        | (rd & 0x1F) << 7
        | 0x03
    )


def encode_store(funct3, rs1, rs2, imm):
    imm &= 0xFFF
    return (
        ((imm >> 5) & 0x7F) << 25
        | (rs2 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (funct3 & 7) << 12
        | (imm & 0x1F) << 7
        | 0x23
    )

def encode_csrrw(rd, rs1, csr):
    return (
        (csr & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (0x1 << 12)
        | (rd & 0x1F) << 7
        | 0x73
    )


def encode_csrrs(rd, rs1, csr):
    return (
        (csr & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (0x2 << 12)
        | (rd & 0x1F) << 7
        | 0x73
    )


def encode_csrrwi(rd, imm, csr):
    return (
        (csr & 0xFFF) << 20
        | (imm & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x73
    )


def encode_vaddvv(vd, vs1, vs2):
    return (
        (0x00 << 26)
        | (vs2 & 0x1F) << 20
        | (vs1 & 0x1F) << 15
        | (0x0 << 12)
        | (vd & 0x1F) << 7
        | 0x57
    )


def encode_vfmavv(vd, vs1, vs2):
    return (
        (0x01 << 26)
        | (vs2 & 0x1F) << 20
        | (vs1 & 0x1F) << 15
        | (0x0 << 12)
        | (vd & 0x1F) << 7
        | 0x57
    )


def encode_vmulvv(vd, vs1, vs2):
    return (
        (0x02 << 26)
        | (vs2 & 0x1F) << 20
        | (vs1 & 0x1F) << 15
        | (0x0 << 12)
        | (vd & 0x1F) << 7
        | 0x57
    )


def encode_vle64(vd, rs1, imm):
    imm &= 0xFFF
    return (
        (imm & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (0x0 << 12)
        | (vd & 0x1F) << 7
        | 0x07
    )


def encode_vse64(vs3, rs1, imm):
    imm &= 0xFFF
    return (
        ((imm >> 5) & 0x7F) << 25
        | (vs3 & 0x1F) << 20
        | (rs1 & 0x1F) << 15
        | (0x0 << 12)
        | (imm & 0x1F) << 7
        | 0x27
    )


def encode_vluxei64(vd, rs1, vs2, scale):
    return (
        ((scale & 0x7) << 29)
        | ((vs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x1 << 12)
        | ((vd & 0x1F) << 7)
        | 0x07
    )


def encode_vsuxei64(vs3, rs1, vs2, scale):
    return (
        ((scale & 0x7) << 29)
        | ((vs3 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x1 << 12)
        | ((vs2 & 0x1F) << 7)
        | 0x27
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

    def test_word_ops(self):
        gm = GoldenModel()
        gm.step(encode_addiw(1, 0, 0xFFF))  # addiw x1,x0,-1
        gm.step(encode_addiw(2, 0, 1))      # addiw x2,x0,1
        gm.step(encode_addw(3, 1, 2))       # addw x3,x1,x2 -> 0
        gm.step(encode_subw(4, 1, 2))       # subw x4,x1,x2 -> -2
        gm.step(encode_slliw(5, 2, 1))      # slliw x5,x2,1 -> 2
        gm.step(encode_srlw(6, 5, 2))       # srlw x6,x5,x2 -> 1
        gm.step(encode_sraiw(7, 4, 1))      # sraiw x7,x4,1 -> -1
        self.assertEqual(gm.regs[3] & 0xFFFFFFFFFFFFFFFF, 0)
        self.assertEqual(gm.regs[4] & 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFE)
        self.assertEqual(gm.regs[5], 2)
        self.assertEqual(gm.regs[6], 1)
        self.assertEqual(gm.regs[7] & 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF)

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

    def test_faddd(self):
        gm = GoldenModel()
        import struct
        gm.fregs[1] = int.from_bytes(struct.pack('<d', 1.5), 'little')
        gm.fregs[2] = int.from_bytes(struct.pack('<d', 2.25), 'little')
        gm.step(encode_faddd(3, 1, 2))
        res = struct.unpack('<d', gm.fregs[3].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, 3.75)

    def test_fsubd_fmuld(self):
        gm = GoldenModel()
        import struct
        gm.fregs[1] = int.from_bytes(struct.pack('<d', 5.0), 'little')
        gm.fregs[2] = int.from_bytes(struct.pack('<d', 1.5), 'little')
        gm.step(encode_fsubd(3, 1, 2))
        sub_res = struct.unpack('<d', gm.fregs[3].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(sub_res, 3.5)
        gm.step(encode_fmuld(4, 1, 2))
        mul_res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(mul_res, 7.5)

    def test_fmaddd(self):
        gm = GoldenModel()
        import struct
        gm.fregs[1] = int.from_bytes(struct.pack('<d', 2.0), 'little')
        gm.fregs[2] = int.from_bytes(struct.pack('<d', 3.0), 'little')
        gm.fregs[3] = int.from_bytes(struct.pack('<d', 4.0), 'little')
        gm.step(encode_fmaddd(4, 1, 2, 3))
        res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, 10.0)

    def test_fmsub_fnmsub_fnmadd(self):
        gm = GoldenModel()
        import struct
        gm.fregs[1] = int.from_bytes(struct.pack('<d', 2.0), 'little')
        gm.fregs[2] = int.from_bytes(struct.pack('<d', 3.0), 'little')
        gm.fregs[3] = int.from_bytes(struct.pack('<d', 4.0), 'little')
        gm.step(encode_fmsubd(4, 1, 2, 3))
        res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, 2.0)
        gm.step(encode_fnmsubd(4, 1, 2, 3))
        res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, -10.0)
        gm.step(encode_fnmaddd(4, 1, 2, 3))
        res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, -2.0)

    def test_fdiv_fmin_fmax(self):
        gm = GoldenModel()
        import struct
        gm.fregs[1] = int.from_bytes(struct.pack('<d', 6.0), 'little')
        gm.fregs[2] = int.from_bytes(struct.pack('<d', 3.0), 'little')
        gm.step(encode_fdivd(3, 1, 2))
        div_res = struct.unpack('<d', gm.fregs[3].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(div_res, 2.0)
        gm.step(encode_fmind(4, 1, 2))
        min_res = struct.unpack('<d', gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(min_res, 3.0)
        gm.step(encode_fmaxd(5, 1, 2))
        max_res = struct.unpack('<d', gm.fregs[5].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(max_res, 6.0)

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
        gm.regs[3] = 6
        gm.step(encode_amoxor(7, 2, 3))  # amoxor.d x7,(x2),x3
        self.assertEqual(gm.regs[7], 9)
        self.assertEqual(gm.mem[0x100], 15)
        gm.regs[3] = 2
        gm.step(encode_amoand(8, 2, 3))  # amoand.d x8,(x2),x3
        self.assertEqual(gm.regs[8], 15)
        self.assertEqual(gm.mem[0x100], 2)
        gm.regs[3] = 8
        gm.step(encode_amoor(9, 2, 3))  # amoor.d x9,(x2),x3
        self.assertEqual(gm.regs[9], 2)
        self.assertEqual(gm.mem[0x100], 10)
        gm.regs[3] = 5
        gm.step(encode_amomin(10, 2, 3))  # amomin.d x10,(x2),x3
        self.assertEqual(gm.regs[10], 10)
        self.assertEqual(gm.mem[0x100], 5)
        gm.regs[3] = 12
        gm.step(encode_amomax(11, 2, 3))  # amomax.d x11,(x2),x3
        self.assertEqual(gm.regs[11], 5)
        self.assertEqual(gm.mem[0x100], 12)
        gm.regs[3] = 7
        gm.step(encode_amominu(12, 2, 3))  # amominu.d x12,(x2),x3
        self.assertEqual(gm.regs[12], 12)
        self.assertEqual(gm.mem[0x100], 7)
        gm.regs[3] = 15
        gm.step(encode_amomaxu(13, 2, 3))  # amomaxu.d x13,(x2),x3
        self.assertEqual(gm.regs[13], 7)
        self.assertEqual(gm.mem[0x100], 15)

    def test_load_store_variants(self):
        gm = GoldenModel()
        for addr in [0x200, 0x202, 0x204, 0x208]:
            gm.load_memory(addr, 0)

        gm.regs[1] = 0x200
        gm.regs[2] = 0xAA
        gm.step(encode_store(0x0, 1, 2, 0))  # sb x2,0(x1)
        gm.step(encode_load(0x0, 3, 1, 0))   # lb x3,0(x1)
        self.assertEqual(gm.regs[3], 0xFFFFFFFFFFFFFFAA)
        gm.step(encode_load(0x4, 4, 1, 0))   # lbu x4,0(x1)
        self.assertEqual(gm.regs[4], 0xAA)
        gm.regs[2] = 0xBEEF
        gm.step(encode_store(0x1, 1, 2, 2))  # sh x2,2(x1)
        gm.step(encode_load(0x1, 5, 1, 2))   # lh x5,2(x1)
        self.assertEqual(gm.regs[5], 0xFFFFFFFFFFFFBEEF)
        gm.step(encode_load(0x5, 6, 1, 2))   # lhu x6,2(x1)
        self.assertEqual(gm.regs[6], 0xBEEF)
        gm.regs[2] = 0x12345678
        gm.step(encode_store(0x2, 1, 2, 4))  # sw x2,4(x1)
        gm.step(encode_load(0x2, 7, 1, 4))   # lw x7,4(x1)
        self.assertEqual(gm.regs[7], 0x12345678)
        gm.step(encode_load(0x6, 8, 1, 4))   # lwu x8,4(x1)
        self.assertEqual(gm.regs[8], 0x12345678)
        gm.regs[2] = 0x1122334455667788
        gm.step(encode_store(0x3, 1, 2, 8))  # sd x2,8(x1)
        gm.step(encode_load(0x3, 9, 1, 8))   # ld x9,8(x1)
        self.assertEqual(gm.regs[9], 0x1122334455667788)

    def test_illegal_instruction_exception(self):
        gm = GoldenModel()
        gm.step(0xffffffff)  # illegal
        self.assertEqual(gm.get_last_exception(), "illegal")

    def test_misaligned_access_exception(self):
        gm = GoldenModel()
        gm.regs[1] = 0x100
        gm.regs[2] = 0xBEEF
        # misaligned halfword store at address 0x101
        gm.step(encode_store(0x1, 1, 2, 1))
        self.assertEqual(gm.get_last_exception(), "misalign")

    def test_page_fault_exception(self):
        gm = GoldenModel()
        gm.regs[1] = 0x500
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), "page")
        gm.regs[2] = 0xAA
        gm.step(encode_store(0x3, 1, 2, 0))
        self.assertEqual(gm.get_last_exception(), "page")

        # misaligned word load at address 0x102
        gm.step(encode_load(0x2, 3, 1, 2))
        self.assertEqual(gm.get_last_exception(), "misalign")

    def test_slt_variants(self):
        gm = GoldenModel()
        # addi x1,x0,5
        gm.step(0x00500093)
        # addi x2,x0,10
        gm.step(0x00a00113)
        # slt x3,x1,x2 -> 1
        slt_instr = (0x00 << 25) | (2 << 20) | (1 << 15) | (0x2 << 12) | (3 << 7) | 0x33
        gm.step(slt_instr)
        self.assertEqual(gm.regs[3], 1)
        # sltu x4,x2,x1 -> 0
        sltu_instr = (0x00 << 25) | (1 << 20) | (2 << 15) | (0x3 << 12) | (4 << 7) | 0x33
        gm.step(sltu_instr)
        self.assertEqual(gm.regs[4], 0)
        # slti x5,x1,8 -> 1
        slti_instr = (8 << 20) | (1 << 15) | (0x2 << 12) | (5 << 7) | 0x13
        gm.step(slti_instr)
        self.assertEqual(gm.regs[5], 1)
        # sltiu x6,x2,5 -> 0
        sltiu_instr = (5 << 20) | (2 << 15) | (0x3 << 12) | (6 << 7) | 0x13
        gm.step(sltiu_instr)
        self.assertEqual(gm.regs[6], 0)

    def test_csr_instructions(self):
        gm = GoldenModel()
        gm.regs[2] = 0x5
        gm.step(encode_csrrw(1, 2, 0x300))  # csrrw x1,csr300,x2
        self.assertEqual(gm.regs[1], 0)
        self.assertEqual(gm.csrs.get(0x300), 0x5)
        gm.regs[3] = 0xA
        gm.step(encode_csrrs(1, 3, 0x300))  # csrrs x1,csr300,x3
        self.assertEqual(gm.regs[1], 0x5)
        self.assertEqual(gm.csrs.get(0x300), 0xF)
        gm.step(encode_csrrwi(4, 0x1, 0x300))  # csrrwi x4,1,csr300
        self.assertEqual(gm.regs[4], 0xF)
        self.assertEqual(gm.csrs.get(0x300), 0x1)

    def test_vector_load_store(self):
        gm = GoldenModel()
        for i in range(8):
            gm.load_memory(0x300 + i * 8, i + 1)
        gm.regs[1] = 0x300
        gm.step(encode_vle64(2, 1, 0))
        for i in range(8):
            self.assertEqual((gm.vregs[2] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, i + 1)
        gm.step(encode_vse64(2, 1, 0x40))
        for i in range(8):
            self.assertEqual(gm.mem[0x340 + i * 8], i + 1)

    def test_vaddvv(self):
        gm = GoldenModel()
        gm.vregs[1] = sum(((i + 1) << (64 * i)) for i in range(8))
        gm.vregs[2] = sum(((10 * (i + 1)) << (64 * i)) for i in range(8))
        gm.step(encode_vaddvv(3, 1, 2))
        for i in range(8):
            expect = (i + 1) + 10 * (i + 1)
            self.assertEqual((gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, expect)

    def test_vfmavv(self):
        gm = GoldenModel()
        gm.vregs[1] = sum(((i + 1) << (64 * i)) for i in range(8))
        gm.vregs[2] = sum(((i + 2) << (64 * i)) for i in range(8))
        gm.vregs[3] = sum(((i + 3) << (64 * i)) for i in range(8))
        gm.step(encode_vfmavv(3, 1, 2))
        for i in range(8):
            expect = (i + 1) * (i + 2) + (i + 3)
            self.assertEqual((gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, expect)

    def test_vmulvv(self):
        gm = GoldenModel()
        gm.vregs[1] = sum(((i + 1) << (64 * i)) for i in range(8))
        gm.vregs[2] = sum(((i + 2) << (64 * i)) for i in range(8))
        gm.step(encode_vmulvv(3, 1, 2))
        for i in range(8):
            expect = (i + 1) * (i + 2)
            self.assertEqual((gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, expect)

    def test_gather_scatter_helpers(self):
        gm = GoldenModel()
        base = 0x500
        idx = [7, 0, 3, 1, 4, 6, 2, 5]
        for i, off in enumerate(idx):
            gm.load_memory(base + off * 8, i + 1)
            gm.load_memory(base + 0x80 + off * 8, 0)
        vec = gm.gather(base, idx, 3)
        for i in range(8):
            self.assertEqual((vec >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, i + 1)
        gm.scatter(base + 0x80, idx, 3, vec)
        for i, off in enumerate(idx):
            self.assertEqual(gm.mem[base + 0x80 + off * 8], i + 1)

    def test_gather_scatter_exceptions(self):
        gm = GoldenModel()
        idx = [0] * 8
        # misaligned gather
        gm.load_memory(0x1000, 1)
        gm.gather(0x1001, idx, 3)
        self.assertEqual(gm.get_last_exception(), "misalign")
        # page fault gather
        gm.gather(0x2000, idx, 3)
        self.assertEqual(gm.get_last_exception(), "page")
        # misaligned scatter
        gm.scatter(0x3001, idx, 3, 0)
        self.assertEqual(gm.get_last_exception(), "misalign")
        # page fault scatter
        gm.scatter(0x4000, idx, 3, 0)
        self.assertEqual(gm.get_last_exception(), "page")

    def test_vluxei_vsuxei(self):
        gm = GoldenModel()
        base = 0x600
        idx = [i * 2 for i in range(8)]
        gm.vregs[1] = sum((off << (64 * i)) for i, off in enumerate(idx))
        for i, off in enumerate(idx):
            gm.load_memory(base + off * 8, i + 1)
            gm.load_memory(base + 0x40 + off * 8, 0)
        gm.regs[2] = base
        gm.step(encode_vluxei64(3, 2, 1, 3))
        for i in range(8):
            self.assertEqual((gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, i + 1)
        gm.vregs[4] = gm.vregs[3]
        gm.regs[2] = base + 0x40
        gm.step(encode_vsuxei64(4, 2, 1, 3))
        for i, off in enumerate(idx):
            self.assertEqual(gm.mem[base + 0x40 + off * 8], i + 1)

    def test_page_table_translation(self):
        gm = GoldenModel()
        # physical location 0x800 mapped to virtual 0x1000
        gm.load_memory(0x800, 0xDEADBEEF, map_va=0x1000)
        gm.regs[1] = 0x1000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.regs[2], 0xDEADBEEF)
        # write should fault due to read-only permission
        gm.map_page(0x2000, 0x900, perm='r')
        gm.regs[1] = 0x2000
        gm.regs[2] = 0x55
        gm.step(encode_store(0x3, 1, 2, 0))
        self.assertEqual(gm.get_last_exception(), 'page')

    def test_virtualized_load_store(self):
        gm = GoldenModel()
        gm.ept.key = 0x1234
        gm.vmcs.vm_on(1)
        # map VA 0x1000 to guest PA 0x800
        gm.map_page(0x1000, 0x800, perm='rw')
        hpa = gm.ept.translate(1, 0x800)
        gm.mem[hpa] = 0xDEAD
        gm.regs[1] = 0x1000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.regs[2], 0xDEAD)
        gm.regs[2] = 0xBEEF
        gm.step(encode_store(0x3, 1, 2, 0))
        self.assertEqual(gm.mem[hpa], 0xBEEF)

    def test_nx_smep_smap_faults(self):
        gm = GoldenModel()
        # NX fault on execute
        gm.map_page(0x1000, 0x1000, perm='r')
        gm.load_memory(0x1000, 0x00000013)
        gm.pc = 0x1000
        gm.step(0x00000013)
        self.assertEqual(gm.get_last_exception(), 'nx')

        # SMEP fault executing user page in kernel mode
        gm.reset(pc=0x2000)
        gm.map_page(0x2000, 0x2000, perm='rwxu')
        gm.load_memory(0x2000, 0x00000013)
        gm.priv_level = 0
        gm.smep = 1
        gm.step(0x00000013)
        self.assertEqual(gm.get_last_exception(), 'smep')

        # SMAP fault on data access to user page in kernel mode
        gm.reset(pc=0)
        gm.map_page(0x3000, 0x3000, perm='ru')
        gm.load_memory(0x3000, 0x55)
        gm.priv_level = 0
        gm.smap = 1
        gm.regs[1] = 0x3000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), 'smap')

    def test_sgx_enclave_fault(self):
        gm = GoldenModel()
        gm.sgx.ecreate(0x1000)
        gm.sgx.eadd(0x1000, 0)
        gm.sgx.einit()
        gm.sgx.eenter()
        gm.load_memory(0x1000, 0xAA, map_va=0x1000)
        gm.load_memory(0x2000, 0xBB, map_va=0x2000)
        gm.regs[1] = 0x1000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertIsNone(gm.get_last_exception())
        self.assertEqual(gm.regs[2], 0xAA)
        gm.regs[1] = 0x2000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), 'sgx')
        gm.sgx.eexit()
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertIsNone(gm.get_last_exception())
        self.assertEqual(gm.regs[2], 0xBB)

    def test_issue_bundle_api(self):
        cov = CoverageModel()
        gm = GoldenModel(coverage=cov)
        insts = [0x00500093,  # addi x1,x0,5
                 0x00a00113]  # addi x2,x0,10
        uops, next_pc, hazards = gm.issue_bundle(0, insts, coverage=cov)
        self.assertEqual(len(uops), 2)
        self.assertEqual(gm.regs[1], 5)
        self.assertEqual(gm.regs[2], 10)
        self.assertEqual(next_pc, 8)
        self.assertEqual(hazards, [])
        summ = cov.summary()
        self.assertGreaterEqual(summ['opcodes'], 1)

    def test_issue_bundle_hazard_detection(self):
        gm = GoldenModel()
        insts = [
            0x00100093,  # addi x1,x0,1
            0x00008133,  # add x2,x1,x0 (RAW hazard on x1)
            0x00200093,  # addi x1,x0,2 (WAW hazard on x1)
        ]
        uops, next_pc, hazards = gm.issue_bundle(0, insts)
        self.assertEqual(next_pc, 12)
        self.assertEqual(len(hazards), 3)
        types = sorted(h['type'] for h in hazards)
        self.assertEqual(types, ['RAW', 'WAR', 'WAW'])

    def test_fence_ecall_ebreak(self):
        gm = GoldenModel()
        gm.step(0x0000000F)  # FENCE
        self.assertIsNone(gm.get_last_exception())
        self.assertEqual(gm.pc, 4)
        gm.step(0x0000100F)  # FENCE.I
        self.assertIsNone(gm.get_last_exception())
        self.assertEqual(gm.pc, 8)
        gm.step(0x00000073)  # ECALL
        self.assertEqual(gm.get_last_exception(), 'ecall')
        gm.step(0x00100073)  # EBREAK
        self.assertEqual(gm.get_last_exception(), 'ebreak')

    def test_spec_fetch_fence(self):
        gm = GoldenModel()
        gm.load_memory(0x100, 0xAA)
        gm.regs[1] = 0x100
        gm.step(encode_spec_fence())
        self.assertEqual(gm.pc, 4)
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), 'spec')
        gm.step(encode_branch(0x0, 0, 0, 8))
        self.assertEqual(gm.pc, 16)
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertIsNone(gm.get_last_exception())
        self.assertEqual(gm.regs[2], 0xAA)

    def test_sev_memory_integration(self):
        gm = GoldenModel()
        gm.set_sev_key(0xDEADBEEFDEADBEEF)
        gm.load_memory(0x1000, 0x55)
        gm.regs[1] = 0x1000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.regs[2], 0x55)
        gm.set_sev_key(0xAB)
        gm.regs[1] = 0x1000
        gm.step(encode_load(0x3, 3, 1, 0))
        self.assertNotEqual(gm.regs[3], 0x55)

    def test_tlb_integration(self):
        cov = CoverageModel()
        gm = GoldenModel(coverage=cov)
        gm.load_memory(0x80001000, 0xAA, map_va=0x4000)
        gm.regs[1] = 0x4000
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.regs[2], 0xAA)
        summary = cov.summary()
        self.assertEqual(summary["tlb_misses"]["L1"], 1)
        self.assertEqual(summary["tlb_misses"]["L2"], 1)
        gm.regs[2] = 0
        gm.step(encode_load(0x3, 2, 1, 0))
        summary = cov.summary()
        self.assertEqual(summary["tlb_hits"]["L1"], 1)

    def test_meltdown_protect(self):
        gm = GoldenModel()
        gm.map_page(0x2000, 0x2000, perm='ru')
        gm.load_memory(0x2000, 0xAA)
        gm.priv_level = 0
        gm.smap = 1
        gm.regs[1] = 0x2000
        gm.set_meltdown_protect(False)
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), 'smap')
        self.assertEqual(gm.regs[2], 0xAA)
        gm.set_meltdown_protect(True)
        gm.regs[2] = 0
        gm.step(encode_load(0x3, 2, 1, 0))
        self.assertEqual(gm.get_last_exception(), 'smap')
        self.assertEqual(gm.regs[2], 0)

if __name__ == '__main__':
    unittest.main()
