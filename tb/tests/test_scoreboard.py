import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components import Scoreboard


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
    def test_commit_sequence(self):
        sb = Scoreboard()
        sb.gm.mem[0x100] = 0

class ScoreboardTest(unittest.TestCase):
    def test_commit_sequence(self):
        sb = Scoreboard()

        # ADDI x1,x0,5
        self.assertTrue(sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4))
        # ADDI x2,x0,0x100
        self.assertTrue(sb.commit(0x10000113, rd_arch=2, rd_val=0x100, next_pc=8))
        # ADD x3,x1,x2 -> 0x105
        self.assertTrue(sb.commit(0x002081b3, rd_arch=3, rd_val=0x105, next_pc=12))
        # Store x3 to 0x100
        sb.commit(0x00312023, is_store=True, store_addr=0x100, store_data=0x105,
                   next_pc=16)
        # Load into x4
        gm = GoldenModel()
        gm.step(0x00500093)
        gm.step(0x10000113)
        gm.step(0x002081b3)
        gm.mem[0x100] = 0x105
        expected = gm.mem.get(0x100, 0)
        # ld x4,0(x2)
        self.assertTrue(sb.commit(0x00013203, rd_arch=4, rd_val=expected,
                                   next_pc=20))
        trace = sb.get_trace()
        self.assertEqual(len(trace), 5)
        self.assertEqual(trace[0]["pc"], 0)
        self.assertEqual(trace[-1]["next_pc"], 20)
        for i, entry in enumerate(trace):
            self.assertEqual(entry["cycle"], i)

    def test_branch_pc(self):
        sb = Scoreboard()
        sb.gm.mem[0x200] = 0

        # JAL to PC+8 at PC=0
        self.assertTrue(sb.commit(0x0080006f, next_pc=8))
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

    def test_commit_order(self):
        sb = Scoreboard()
        self.assertTrue(sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4, rob_idx=0))
        self.assertTrue(sb.commit(0x00300113, rd_arch=2, rd_val=3, next_pc=8, rob_idx=1))
        # Out-of-order commit should fail
        self.assertFalse(sb.commit(0x00000013, rd_arch=0, rd_val=0, next_pc=12, rob_idx=1))


    def test_reset(self):
        sb = Scoreboard()
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        sb.reset()
        self.assertEqual(sb.cycle, 0)
        self.assertEqual(len(sb.get_trace()), 0)
        self.assertTrue(sb.commit(0x00300113, rd_arch=2, rd_val=3, next_pc=4))

    def test_illegal_exception(self):
        sb = Scoreboard()
        # 0xffffffff is not a valid instruction
        self.assertTrue(sb.commit(0xffffffff, exception="illegal"))
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
        # access unmapped memory at 0x500
        self.assertTrue(
            sb.commit(
                encode_load(0x3, 1, 0, 0x500),
                exception="page",
            )
        )
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

    def test_byte_load_store(self):
        sb = Scoreboard()

        # addi x1,x0,0x200
        self.assertTrue(sb.commit(0x20000093, rd_arch=1, rd_val=0x200, next_pc=4))
        # addi x2,x0,0xAA
        self.assertTrue(sb.commit(0x0AA00113, rd_arch=2, rd_val=0xAA, next_pc=8))
        # sb x2,0(x1)

        sb.commit(encode_store(0x0, 1, 2, 0), is_store=True, store_addr=0x200, store_data=0xAA, next_pc=12)
        # lb x3,0(x1)
        self.assertTrue(sb.commit(encode_load(0x0, 3, 1, 0), rd_arch=3, rd_val=0xFFFFFFFFFFFFFFAA, next_pc=16))

        sb.commit(0x00210023, is_store=True, store_addr=0x200, store_data=0xAA, next_pc=12)
        # lb x3,0(x1)
        self.assertTrue(sb.commit(0x00010183, rd_arch=3, rd_val=0xFFFFFFFFFFFFFFAA, next_pc=16))


    def test_load_data_check(self):
        sb = Scoreboard()
        # addi x1,x0,0x300
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
        # beq x0,x0,+8 (taken)
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
        # Another branch mispredicted
        instr2 = encode_branch(0x1, 0, 0, 8)  # bne x0,x0,+8 -> not taken
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
        sb.dump_trace(trace_file)
        with open(trace_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        os.remove(trace_file)
        self.assertTrue(lines[0].strip().endswith("rob_idx"))
        self.assertEqual(len(lines), 2)

    def test_coverage_hook(self):
        cov = CoverageModel()
        sb = Scoreboard(coverage=cov)
        sb.commit(0x00500093, rd_arch=1, rd_val=5, next_pc=4)
        sb.commit(0xffffffff, exception="illegal")
        # branch predicted correctly
        sb.commit(
            encode_branch(0x0, 0, 0, 8),
            branch_taken=True,
            branch_target=8,
            pred_taken=True,
            pred_target=8,
            mispredict=False,
            next_pc=8,
        )
        # mispredicted branch
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
        self.assertEqual(summary['opcodes'], 3)
        self.assertEqual(summary['exceptions']['illegal'], 1)
        self.assertEqual(summary['branches'], 2)
        self.assertEqual(summary['mispredicts'], 1)

        self.assertTrue(lines[0].startswith("cycle"))
        self.assertEqual(len(lines), 2)


if __name__ == '__main__':
    unittest.main()
