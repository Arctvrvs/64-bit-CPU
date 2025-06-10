import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components import Scoreboard
from tb.uvm_components.trace_utils import load_trace
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


def encode_load(funct3, rd, rs1, imm):
    imm &= 0xFFF
    return (
        (imm & 0xFFF) << 20
        | (rs1 & 0x1F) << 15
        | (funct3 & 7) << 12
        | (rd & 0x1F) << 7
        | 0x03
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


if __name__ == "__main__":
    unittest.main()
