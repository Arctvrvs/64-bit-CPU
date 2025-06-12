import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components import Scoreboard
from tb.uvm_components.trace_utils import load_trace, load_trace_json
from tb.uvm_components.coverage import CoverageModel
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

def encode_lr(rd, rs1):
    return (
        (0x02 << 27)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_sc(rd, rs1, rs2):
    return (
        (0x03 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amoadd(rd, rs1, rs2):
    return (
        (0x00 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amoswap(rd, rs1, rs2):
    return (
        (0x01 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amoxor(rd, rs1, rs2):
    return (
        (0x04 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amoand(rd, rs1, rs2):
    return (
        (0x0C << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amoor(rd, rs1, rs2):
    return (
        (0x08 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amomin(rd, rs1, rs2):
    return (
        (0x10 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amomax(rd, rs1, rs2):
    return (
        (0x14 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amominu(rd, rs1, rs2):
    return (
        (0x18 << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_amomaxu(rd, rs1, rs2):
    return (
        (0x1C << 27)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x3 << 12)
        | ((rd & 0x1F) << 7)
        | 0x2F
    )

def encode_addw(rd, rs1, rs2):
    return (
        ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x3B
    )

def encode_subw(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x3B
    )

def encode_sllw(rd, rs1, rs2):
    return (
        ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x1 << 12)
        | ((rd & 0x1F) << 7)
        | 0x3B
    )

def encode_srlw(rd, rs1, rs2):
    return (
        ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x5 << 12)
        | ((rd & 0x1F) << 7)
        | 0x3B
    )

def encode_sraw(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x5 << 12)
        | ((rd & 0x1F) << 7)
        | 0x3B
    )

def encode_addiw(rd, rs1, imm):
    imm &= 0xFFF
    return (
        ((imm & 0xFFF) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x1B
    )

def encode_slliw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x00 << 25)
        | ((shamt & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x1 << 12)
        | ((rd & 0x1F) << 7)
        | 0x1B
    )

def encode_srliw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x00 << 25)
        | ((shamt & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x5 << 12)
        | ((rd & 0x1F) << 7)
        | 0x1B
    )

def encode_sraiw(rd, rs1, shamt):
    shamt &= 0x1F
    return (
        (0x20 << 25)
        | ((shamt & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x5 << 12)
        | ((rd & 0x1F) << 7)
        | 0x1B
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

def encode_spec_fence():
    return 0x0000200F


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


def encode_vfmavv(vd, vs1, vs2):
    return (
        (0x01 << 26)
        | ((vs2 & 0x1F) << 20)
        | ((vs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((vd & 0x1F) << 7)
        | 0x57
    )


def encode_vmulvv(vd, vs1, vs2):
    return (
        (0x02 << 26)
        | ((vs2 & 0x1F) << 20)
        | ((vs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((vd & 0x1F) << 7)
        | 0x57
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


def encode_faddd(rd, rs1, rs2, rm=0):
    return (
        (0x01 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fsubd(rd, rs1, rs2, rm=0):
    return (
        (0x05 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fmuld(rd, rs1, rs2, rm=0):
    return (
        (0x09 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fdivd(rd, rs1, rs2, rm=0):
    return (
        (0x0D << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fmind(rd, rs1, rs2, rm=0):
    return (
        (0x15 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fmaxd(rd, rs1, rs2, rm=1):
    return (
        (0x15 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x53
    )


def encode_fmaddd(rd, rs1, rs2, rs3, rm=0):
    return (
        ((rs3 & 0x1F) << 27)
        | (0x1 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x43
    )


def encode_fmsubd(rd, rs1, rs2, rs3, rm=0):
    return (
        ((rs3 & 0x1F) << 27)
        | (0x1 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x47
    )


def encode_fnmsubd(rd, rs1, rs2, rs3, rm=0):
    return (
        ((rs3 & 0x1F) << 27)
        | (0x1 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x4B
    )


def encode_fnmaddd(rd, rs1, rs2, rs3, rm=0):
    return (
        ((rs3 & 0x1F) << 27)
        | (0x1 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((rm & 7) << 12)
        | ((rd & 0x1F) << 7)
        | 0x4F
    )


def encode_csrrwi(rd, imm, csr):
    return (
        (csr & 0xFFF) << 20
        | (imm & 0x1F) << 15
        | (0x5 << 12)
        | (rd & 0x1F) << 7
        | 0x73
    )


class ScoreboardTest(unittest.TestCase):
    def test_matches(self):
        sb = Scoreboard()
        sb.add_expected(1)
        sb.add_expected(2)
        sb.add_actual(1)
        sb.add_actual(2)
        self.assertTrue(sb.check())

    def test_mismatch(self):
        sb = Scoreboard()
        sb.add_expected(1)
        sb.add_actual(2)
        self.assertFalse(sb.check())

    def test_commit_sequence(self):
        sb = Scoreboard()
        sb.gm.mem[0x100] = 0
        self.assertTrue(sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4))
        self.assertTrue(sb.commit(0x10000113, rd_arch=2, rd_val=0x100, next_pc=8))
        self.assertTrue(sb.commit(0x002081b3, rd_arch=3, rd_val=0x105, next_pc=12))
        sb.commit(0x00312023, is_store=True, store_addr=0x100, store_data=0x105, next_pc=16)
        gm = GoldenModel()
        gm.step(0x00500093)
        gm.step(0x10000113)
        gm.step(0x002081b3)
        gm.mem[0x100] = 0x105
        expected = gm.mem.get(0x100, 0)
        self.assertTrue(sb.commit(0x00013203, rd_arch=4, rd_val=expected, next_pc=20))
        trace = sb.get_trace()
        self.assertEqual(len(trace), 5)
        self.assertEqual(trace[0]["pc"], 0)
        self.assertEqual(trace[-1]["next_pc"], 20)
        for i, entry in enumerate(trace):
            self.assertEqual(entry["cycle"], i)

    def test_branch_pc(self):
        sb = Scoreboard()
        sb.gm.mem[0x200] = 0
        self.assertTrue(sb.commit(0x0080006F, next_pc=8))
        trace = sb.get_trace()
        self.assertEqual(trace[0]["cycle"], 0)

    def test_commit_bundle(self):
        sb = Scoreboard()
        instrs = [0x00500093, 0x00300113]
        results = sb.commit_bundle(
            instrs,
            rd_arch_list=[1, 2],
            rd_val_list=[5, 3],
            next_pc_list=[4, 8],
            exception_list=[None, None],
            branch_taken_list=[False, False],
            branch_target_list=[None, None],
            pred_taken_list=[False, False],
            pred_target_list=[None, None],
            mispredict_list=[False, False],
            rob_idx_list=[0, 1],
        )
        self.assertEqual(results, [True, True])
        trace = sb.get_trace()
        self.assertEqual(len(trace), 2)
        self.assertEqual(trace[0]["cycle"], 0)
        self.assertEqual(trace[1]["cycle"], 0)
        self.assertEqual(sb.cycle, 1)

    def test_commit_bundle_8wide(self):
        sb = Scoreboard()
        instrs = [
            0x00100093,
            0x00200113,
            0x00300193,
            0x00400213,
            0x00500293,
            0x00600313,
            0x00700393,
            0x00800413,
        ]
        rd_arch = list(range(1, 9))
        rd_val = list(range(1, 9))
        results = sb.commit_bundle(
            instrs,
            rd_arch_list=rd_arch,
            rd_val_list=rd_val,
            next_pc_list=[4 * (i + 1) for i in range(8)],
            rob_idx_list=list(range(8)),
        )
        self.assertEqual(results, [True] * 8)
        self.assertEqual(len(sb.get_trace()), 8)
        for entry in sb.get_trace():
            self.assertEqual(entry["cycle"], 0)
        self.assertEqual(sb.cycle, 1)

    def test_commit_order(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4, rob_idx=0))
        self.assertTrue(sb.commit(0x00300113, rd_arch=2, rd_val=3, next_pc=8, rob_idx=1))
        self.assertFalse(sb.commit(0x00000013, rd_arch=0, rd_val=0, next_pc=12, rob_idx=1))

    def test_commit_bundle_order(self):
        sb = Scoreboard()
        instrs1 = [0x00100093, 0x00200113]
        instrs2 = [0x00300193, 0x00400213]
        res1 = sb.commit_bundle(instrs1, rd_arch_list=[1, 2], rd_val_list=[1, 2], rob_idx_list=[0, 1])
        self.assertEqual(res1, [True, True])
        res2 = sb.commit_bundle(instrs2, rd_arch_list=[3, 4], rd_val_list=[3, 4], rob_idx_list=[2, 3])
        self.assertEqual(res2, [True, True])
        self.assertEqual(sb.expected_rob_idx, 4)
        sb.reset()
        sb.commit_bundle(instrs1, rd_arch_list=[1, 2], rd_val_list=[1, 2], rob_idx_list=[0, 1])
        res_bad = sb.commit_bundle(instrs2, rd_arch_list=[3, 4], rd_val_list=[3, 4], rob_idx_list=[2, 4])
        self.assertEqual(res_bad, [True, False])

    def test_reset(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        sb.reset()
        self.assertEqual(sb.cycle, 0)
        self.assertEqual(len(sb.get_trace()), 0)
        self.assertTrue(sb.commit(0x00300113, rd_arch=2, rd_val=3, next_pc=4))

    def test_illegal_exception(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0xFFFFFFFF, exception="illegal"))
        trace = sb.get_trace()
        self.assertEqual(trace[0]["exception"], "illegal")

    def test_misaligned_exception(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0x10000093, rd_arch=1, rd_val=0x100, next_pc=4))
        self.assertTrue(sb.commit(0x0AA00113, rd_arch=2, rd_val=0xAA, next_pc=8))
        self.assertTrue(sb.commit(encode_store(0x1, 1, 2, 1), exception="misalign"))
        self.assertTrue(sb.commit(encode_load(0x2, 3, 1, 2), exception="misalign"))

    def test_page_fault_exception(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(encode_load(0x3, 1, 0, 0x500), exception="page"))
        self.assertTrue(
            sb.commit(
                encode_store(0x3, 0, 1, 0x500),
                is_store=True,
                store_addr=0x500,
                store_data=0,
                exception="page",
            )
        )

    def test_byte_load_store(self):
        sb = Scoreboard()
        sb.gm.mem[0x200] = 0
        self.assertTrue(sb.commit(0x20000093, rd_arch=1, rd_val=0x200, next_pc=4))
        self.assertTrue(sb.commit(0x0AA00113, rd_arch=2, rd_val=0xAA, next_pc=8))
        sb.commit(encode_store(0x0, 1, 2, 0), is_store=True, store_addr=0x200, store_data=0xAA, next_pc=12)
        self.assertTrue(sb.commit(encode_load(0x0, 3, 1, 0), rd_arch=3, rd_val=0xFFFFFFFFFFFFFFAA, next_pc=16))

    def test_load_data_check(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0x30000093, rd_arch=1, rd_val=0x300, next_pc=4))
        sb.gm.mem[0x300] = 0x1122334455667788
        ld_instr = encode_load(0x3, 2, 1, 0)
        self.assertTrue(
            sb.commit(
                ld_instr,
                rd_arch=2,
                rd_val=0x1122334455667788,
                is_load=True,
                load_addr=0x300,
                load_data=0x1122334455667788,
                next_pc=8,
            )
        )

    def test_branch_prediction(self):
        sb = Scoreboard()
        instr = encode_branch(0x0, 0, 0, 8)
        self.assertTrue(
            sb.commit(
                instr,
                branch_taken=True,
                branch_target=8,
                pred_taken=True,
                pred_target=8,
                mispredict=False,
                next_pc=8,
            )
        )
        instr2 = encode_branch(0x1, 0, 0, 8)
        self.assertTrue(
            sb.commit(
                instr2,
                branch_taken=False,
                branch_target=None,
                pred_taken=True,
                pred_target=16,
                mispredict=True,
                next_pc=12,
            )
        )

    def test_csr_commit(self):
        sb = Scoreboard()
        instr = encode_csrrwi(1, 2, 0x300)
        self.assertTrue(sb.commit(instr, rd_arch=1, rd_val=0, next_pc=4))
        self.assertEqual(sb.gm.csrs.get(0x300), 2)

    def test_dump_trace(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        trace_file = os.path.join(os.path.dirname(__file__), "trace.csv")
        returned = sb.dump_trace(trace_file)
        with open(trace_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        os.remove(trace_file)
        self.assertTrue(lines[0].strip().endswith("rob_idx"))
        self.assertEqual(len(lines), 2)
        self.assertEqual(returned, sb.get_trace())

    def test_dump_trace_round_trip(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        tmp = os.path.join(os.path.dirname(__file__), "trace_rt.csv")
        ret = sb.dump_trace(tmp)
        loaded = load_trace(tmp)
        os.remove(tmp)
        self.assertEqual(loaded, ret)

    def test_dump_trace_json(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        tmp = os.path.join(os.path.dirname(__file__), "trace_rt.json")
        ret = sb.dump_trace_json(tmp)
        loaded = load_trace_json(tmp)
        os.remove(tmp)
        self.assertEqual(loaded, ret)

    def test_dump_coverage(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        tmp = os.path.join(os.path.dirname(__file__), "cov.json")
        summary = sb.dump_coverage(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            data = json.load(f)
        os.remove(tmp)
        self.assertEqual(data["opcodes"], 1)
        self.assertEqual(summary["opcodes"], 1)

    def test_dump_coverage_no_model(self):
        sb = Scoreboard()
        tmp = os.path.join(os.path.dirname(__file__), "no_cov.json")
        summary = sb.dump_coverage(tmp)
        self.assertEqual(summary, {})
        self.assertFalse(os.path.exists(tmp))

    def test_coverage_hook(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        sb.commit(0xFFFFFFFF, exception="illegal")
        sb.commit(
            encode_branch(0x0, 0, 0, 8),
            branch_taken=True,
            branch_target=8,
            pred_taken=True,
            pred_target=8,
            mispredict=False,
            next_pc=8,
        )
        sb.commit(
            encode_branch(0x1, 0, 0, 8),
            branch_taken=False,
            branch_target=None,
            pred_taken=True,
            pred_target=16,
            mispredict=True,
            next_pc=12,
        )
        summary = cov.summary()
        self.assertEqual(summary["opcodes"], 3)
        self.assertGreaterEqual(summary["immediates"], 2)
        self.assertEqual(summary["exceptions"]["illegal"], 1)
        self.assertEqual(summary["branches"], 2)
        self.assertEqual(summary["mispredicts"], 1)

    def test_reset_clears_coverage(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        self.assertEqual(cov.summary()["opcodes"], 1)
        sb.reset()
        self.assertEqual(cov.summary()["opcodes"], 0)

    def test_get_coverage_summary(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        summary = sb.get_coverage_summary()
        self.assertEqual(summary["opcodes"], 1)

    def test_get_coverage_summary_no_model(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        summary = sb.get_coverage_summary()
        self.assertEqual(summary, {})

    def test_vector_gather_scatter_helpers(self):
        sb = Scoreboard()
        base = 0x800
        idx = [7, 0, 3, 1, 4, 6, 2, 5]
        for i, off in enumerate(idx):
            sb.gm.load_memory(base + off * 8, i + 1)
            sb.gm.load_memory(base + 0x40 + off * 8, 0)
        vec = sb.gm.gather(base, idx, 3)
        self.assertTrue(sb.check_gather(base, idx, 3, vec))
        self.assertTrue(sb.check_scatter(base + 0x40, idx, 3, vec))
        for i, off in enumerate(idx):
            self.assertEqual(sb.gm.mem[base + 0x40 + off * 8], i + 1)

    def test_vector_coverage_counters(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        base = 0x900
        idx = list(range(8))
        for i in range(8):
            sb.gm.load_memory(base + i * 8, i)
            sb.gm.load_memory(base + 0x80 + i * 8, 0)
        vec = sb.gm.gather(base, idx, 3)
        sb.check_gather(base, idx, 3, vec)
        sb.check_scatter(base + 0x80, idx, 3, vec)
        summary = cov.summary()
        self.assertEqual(summary["vector_gathers"], 1)
        self.assertEqual(summary["vector_scatters"], 1)

    def test_vector_load_store_coverage(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        base = 0xA00
        for i in range(8):
            sb.gm.load_memory(base + i * 8, i + 1)
        sb.gm.regs[1] = base
        sb.commit(encode_vle64(2, 1, 0))
        sb.commit(encode_vse64(2, 1, 0))
        summary = cov.summary()
        self.assertEqual(summary["vector_loads"], 1)
        self.assertEqual(summary["vector_stores"], 1)

    def test_ecall_ebreak(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0x00000073, exception="ecall"))
        self.assertTrue(sb.commit(0x00100073, exception="ebreak"))

    def test_vluxei_vsuxei_coverage(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        base = 0xB00
        idx = [i * 2 for i in range(8)]
        sb.gm.vregs[1] = sum((off << (64 * i)) for i, off in enumerate(idx))
        for i, off in enumerate(idx):
            sb.gm.load_memory(base + off * 8, i + 1)
            sb.gm.load_memory(base + 0x40 + off * 8, 0)
        sb.gm.regs[2] = base
        sb.commit(encode_vluxei64(3, 2, 1, 3))
        sb.gm.vregs[4] = sb.gm.vregs[3]
        sb.gm.regs[2] = base + 0x40
        sb.commit(encode_vsuxei64(4, 2, 1, 3))
        for i, off in enumerate(idx):
            self.assertEqual(sb.gm.mem[base + 0x40 + off * 8], i + 1)
        summary = cov.summary()
        self.assertEqual(summary["vector_loads"], 1)
        self.assertEqual(summary["vector_stores"], 1)

    def test_floating_point_ops(self):
        sb = Scoreboard()
        import struct
        sb.gm.fregs[1] = int.from_bytes(struct.pack('<d', 2.0), 'little')
        sb.gm.fregs[2] = int.from_bytes(struct.pack('<d', 0.5), 'little')
        self.assertTrue(sb.commit(encode_faddd(3, 1, 2)))
        add_res = struct.unpack('<d', sb.gm.fregs[3].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(add_res, 2.5)
        self.assertTrue(sb.commit(encode_fsubd(4, 1, 2)))
        sub_res = struct.unpack('<d', sb.gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(sub_res, 1.5)
        self.assertTrue(sb.commit(encode_fmuld(5, 1, 2)))
        mul_res = struct.unpack('<d', sb.gm.fregs[5].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(mul_res, 1.0)
        self.assertTrue(sb.commit(encode_fdivd(6, 1, 2)))
        div_res = struct.unpack('<d', sb.gm.fregs[6].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(div_res, 4.0)
        self.assertTrue(sb.commit(encode_fmind(7, 1, 2)))
        min_res = struct.unpack('<d', sb.gm.fregs[7].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(min_res, 0.5)
        self.assertTrue(sb.commit(encode_fmaxd(8, 1, 2)))
        max_res = struct.unpack('<d', sb.gm.fregs[8].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(max_res, 2.0)

    def test_fmaddd(self):
        sb = Scoreboard()
        import struct
        sb.gm.fregs[1] = int.from_bytes(struct.pack('<d', 2.0), 'little')
        sb.gm.fregs[2] = int.from_bytes(struct.pack('<d', 3.0), 'little')
        sb.gm.fregs[3] = int.from_bytes(struct.pack('<d', 4.0), 'little')
        self.assertTrue(sb.commit(encode_fmaddd(4, 1, 2, 3)))
        res = struct.unpack('<d', sb.gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, 10.0)

    def test_fmsub_fnmsub_fnmadd(self):
        sb = Scoreboard()
        import struct
        sb.gm.fregs[1] = int.from_bytes(struct.pack('<d', 2.0), 'little')
        sb.gm.fregs[2] = int.from_bytes(struct.pack('<d', 3.0), 'little')
        sb.gm.fregs[3] = int.from_bytes(struct.pack('<d', 4.0), 'little')
        self.assertTrue(sb.commit(encode_fmsubd(4, 1, 2, 3)))
        res = struct.unpack('<d', sb.gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, 2.0)
        self.assertTrue(sb.commit(encode_fnmsubd(4, 1, 2, 3)))
        res = struct.unpack('<d', sb.gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, -10.0)
        self.assertTrue(sb.commit(encode_fnmaddd(4, 1, 2, 3)))
        res = struct.unpack('<d', sb.gm.fregs[4].to_bytes(8, 'little'))[0]
        self.assertAlmostEqual(res, -2.0)

    def test_word_ops(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(encode_addiw(1, 0, 0xFFF), rd_arch=1, rd_val=0xFFFFFFFFFFFFFFFF))
        self.assertTrue(sb.commit(encode_addiw(2, 0, 1), rd_arch=2, rd_val=1))
        self.assertTrue(sb.commit(encode_addw(3, 1, 2), rd_arch=3, rd_val=0))
        self.assertTrue(sb.commit(encode_subw(4, 1, 2), rd_arch=4, rd_val=0xFFFFFFFFFFFFFFFE))
        self.assertTrue(sb.commit(encode_slliw(5, 2, 1), rd_arch=5, rd_val=2))
        self.assertTrue(sb.commit(encode_srlw(6, 5, 2), rd_arch=6, rd_val=1))
        self.assertTrue(sb.commit(encode_sraiw(7, 4, 1), rd_arch=7, rd_val=0xFFFFFFFFFFFFFFFF))

    def test_vector_fma(self):
        sb = Scoreboard()
        sb.gm.vregs[1] = sum(((i + 1) << (64 * i)) for i in range(8))
        sb.gm.vregs[2] = sum(((i + 2) << (64 * i)) for i in range(8))
        sb.gm.vregs[3] = sum(((i + 3) << (64 * i)) for i in range(8))
        self.assertTrue(sb.commit(encode_vfmavv(3, 1, 2)))
        for i in range(8):
            expect = (i + 1) * (i + 2) + (i + 3)
            self.assertEqual((sb.gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, expect)

    def test_vector_mul(self):
        sb = Scoreboard()
        sb.gm.vregs[1] = sum(((i + 1) << (64 * i)) for i in range(8))
        sb.gm.vregs[2] = sum(((i + 2) << (64 * i)) for i in range(8))
        self.assertTrue(sb.commit(encode_vmulvv(3, 1, 2)))
        for i in range(8):
            expect = (i + 1) * (i + 2)
            self.assertEqual((sb.gm.vregs[3] >> (64 * i)) & 0xFFFFFFFFFFFFFFFF, expect)

    def test_atomic_operations(self):
        sb = Scoreboard()
        sb.gm.regs[2] = 0x100
        sb.gm.load_memory(0x100, 5)
        self.assertTrue(sb.commit(encode_lr(1, 2), rd_arch=1, rd_val=5))
        sb.gm.regs[3] = 7
        self.assertTrue(
            sb.commit(
                encode_sc(4, 2, 3),
                rd_arch=4,
                rd_val=0,
                is_store=True,
                store_addr=0x100,
                store_data=7,
            )
        )
        sb.gm.regs[3] = 9
        sb.gm.regs[2] = 0x108
        self.assertTrue(sb.commit(encode_sc(4, 2, 3), rd_arch=4, rd_val=1))
        sb.gm.regs[2] = 0x100
        self.assertTrue(
            sb.commit(
                encode_amoadd(5, 2, 3),
                rd_arch=5,
                rd_val=7,
                is_store=True,
                store_addr=0x100,
                store_data=16,
            )
        )
        sb.gm.regs[3] = 9
        self.assertTrue(
            sb.commit(
                encode_amoswap(6, 2, 3),
                rd_arch=6,
                rd_val=16,
                is_store=True,
                store_addr=0x100,
                store_data=9,
            )
        )
        sb.gm.regs[3] = 6
        self.assertTrue(
            sb.commit(
                encode_amoxor(7, 2, 3),
                rd_arch=7,
                rd_val=9,
                is_store=True,
                store_addr=0x100,
                store_data=15,
            )
        )
        sb.gm.regs[3] = 2
        self.assertTrue(
            sb.commit(
                encode_amoand(8, 2, 3),
                rd_arch=8,
                rd_val=15,
                is_store=True,
                store_addr=0x100,
                store_data=2,
            )
        )
        sb.gm.regs[3] = 8
        self.assertTrue(
            sb.commit(
                encode_amoor(9, 2, 3),
                rd_arch=9,
                rd_val=2,
                is_store=True,
                store_addr=0x100,
                store_data=10,
            )
        )
        sb.gm.regs[3] = 5
        self.assertTrue(
            sb.commit(
                encode_amomin(10, 2, 3),
                rd_arch=10,
                rd_val=10,
                is_store=True,
                store_addr=0x100,
                store_data=5,
            )
        )
        sb.gm.regs[3] = 12
        self.assertTrue(
            sb.commit(
                encode_amomax(11, 2, 3),
                rd_arch=11,
                rd_val=5,
                is_store=True,
                store_addr=0x100,
                store_data=12,
            )
        )
        sb.gm.regs[3] = 7
        self.assertTrue(
            sb.commit(
                encode_amominu(12, 2, 3),
                rd_arch=12,
                rd_val=12,
                is_store=True,
                store_addr=0x100,
                store_data=7,
            )
        )
        sb.gm.regs[3] = 15
        self.assertTrue(
            sb.commit(
                encode_amomaxu(13, 2, 3),
                rd_arch=13,
                rd_val=7,
                is_store=True,
                store_addr=0x100,
                store_data=15,
            )
        )

    def test_vector_gather_scatter_exceptions(self):
        sb = Scoreboard()
        idx = [0] * 8
        sb.gm.load_memory(0x1000, 1)
        # misaligned gather should fail
        self.assertFalse(sb.check_gather(0x1001, idx, 3, 0))
        # page fault gather should fail
        self.assertFalse(sb.check_gather(0x2000, idx, 3, 0))
        # misaligned scatter should fail
        self.assertFalse(sb.check_scatter(0x3001, idx, 3, 0))
        # page fault scatter should fail
        self.assertFalse(sb.check_scatter(0x4000, idx, 3, 0))

    def test_nx_smep_smap_in_scoreboard(self):
        sb = Scoreboard()
        # NX on fetch
        sb.gm.map_page(0x1000, 0x1000, perm='r')
        sb.gm.load_memory(0x1000, 0x00000013)
        sb.gm.pc = 0x1000
        self.assertTrue(
            sb.commit(0x00000013, next_pc=0x1004, exception="nx")
        )

        # SMEP fault
        sb.reset(pc=0x2000)
        sb.gm.map_page(0x2000, 0x2000, perm='rwxu')
        sb.gm.load_memory(0x2000, 0x00000013)
        sb.gm.priv_level = 0
        sb.gm.smep = 1
        self.assertTrue(
            sb.commit(0x00000013, next_pc=0x2004, exception="smep")
        )

        # SMAP fault on load
        sb.reset()
        sb.gm.map_page(0x3000, 0x3000, perm='ru')
        sb.gm.load_memory(0x3000, 0x55)
        sb.gm.priv_level = 0
        sb.gm.smap = 1
        sb.gm.regs[1] = 0x3000
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                is_load=True,
                load_addr=0x3000,
                load_data=0x55,
                exception="smap",
            )
        )

    def test_spec_fetch_fence_in_scoreboard(self):
        sb = Scoreboard()
        sb.gm.load_memory(0x100, 0xAA)
        sb.gm.regs[1] = 0x100
        self.assertTrue(sb.commit(encode_spec_fence(), next_pc=4))
        self.assertTrue(sb.commit(encode_load(0x3, 2, 1, 0), next_pc=8, exception="spec"))
        self.assertTrue(
            sb.commit(
                encode_branch(0x0, 0, 0, 8),
                branch_taken=True,
                branch_target=16,
                next_pc=16,
            )
        )
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0xAA,
                is_load=True,
                load_addr=0x100,
                load_data=0xAA,
                next_pc=20,
            )
        )

    def test_sev_memory_integration(self):
        sb = Scoreboard()
        sb.gm.set_sev_key(0x12345678)
        sb.gm.load_memory(0x2000, 0x66)
        sb.gm.regs[1] = 0x2000
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0x66,
                is_load=True,
                load_addr=0x2000,
                load_data=0x66,
                next_pc=4,
            )
        )
        sb.gm.set_sev_key(0x9999)
        sb.gm.regs[1] = 0x2000
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 3, 1, 0),
                rd_arch=3,
                rd_val=0,
                is_load=True,
                load_addr=0x2000,
                load_data=0x9999,
                next_pc=8,
                exception="page",
            )
        )

    def test_meltdown_protect(self):
        sb = Scoreboard()
        sb.gm.map_page(0x3000, 0x3000, perm="ru")
        sb.gm.load_memory(0x3000, 0xAA)
        sb.gm.priv_level = 0
        sb.gm.smap = 1
        sb.gm.regs[1] = 0x3000
        sb.gm.set_meltdown_protect(False)
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0xAA,
                is_load=True,
                load_addr=0x3000,
                load_data=0xAA,
                exception="smap",
            )
        )
        sb.gm.set_meltdown_protect(True)
        sb.gm.regs[1] = 0x3000
        sb.gm.regs[2] = 0
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0,
                is_load=True,
                load_addr=0x3000,
                load_data=0xAA,
                exception="smap",
            )
        )

    def test_tlb_coverage(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.gm.load_memory(0x80004000, 0x55, map_va=0x4000)
        sb.gm.regs[1] = 0x4000
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0x55,
                is_load=True,
                load_addr=0x80004000,
                load_data=0x55,
                next_pc=4,
            )
        )
        summary = sb.get_coverage_summary()
        self.assertEqual(summary["tlb_misses"]["L1"], 1)
        self.assertEqual(summary["tlb_misses"]["L2"], 1)
        sb.gm.regs[2] = 0
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0x55,
                is_load=True,
                load_addr=0x80004000,
                load_data=0x55,
                next_pc=8,
            )
        )
        summary = sb.get_coverage_summary()
        self.assertEqual(summary["tlb_hits"]["L1"], 1)

    def test_virtualized_load_store(self):
        sb = Scoreboard()
        sb.gm.ept.key = 0x1234
        sb.gm.vmcs.vm_on(1)
        sb.gm.map_page(0x1000, 0x800, perm="rw")
        hpa = sb.gm.ept.translate(1, 0x800)
        sb.gm.mem[hpa] = 0xDEAD
        sb.gm.regs[1] = 0x1000
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 2, 1, 0),
                rd_arch=2,
                rd_val=0xDEAD,
                is_load=True,
                load_addr=hpa,
                load_data=0xDEAD,
                next_pc=4,
            )
        )
        sb.gm.regs[2] = 0xBEEF
        self.assertTrue(
            sb.commit(
                encode_store(0x3, 1, 2, 0),
                is_store=True,
                store_addr=hpa,
                store_data=0xBEEF,
                next_pc=8,
            )
        )


if __name__ == "__main__":
    unittest.main()
