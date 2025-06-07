import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rob_rs_iq.issue_queue import IssueQueue

class IssueQueueTest(unittest.TestCase):
    def test_basic_alloc_issue(self):
        iq = IssueQueue(entries=8, issue_width=4)
        iq.alloc([
            {"valid": True, "func_type": 0, "op1": 1, "op2": 2, "dest": 5, "rob_idx": 0,
             "src1_tag": 1, "src2_tag": 2, "ready1": True, "ready2": True, "pred_mask": 0xFF},
            {"valid": True, "func_type": 0, "op1": 3, "op2": 4, "dest": 6, "rob_idx": 1,
             "src1_tag": 3, "src2_tag": 4, "ready1": True, "ready2": True, "pred_mask": 0xFF},
        ])
        issued = iq.issue({"int": 2})
        self.assertEqual(len(issued), 2)
        self.assertEqual(issued[0]["dest"], 5)
        self.assertEqual(issued[1]["dest"], 6)
        self.assertEqual(iq.count, 0)

    def test_issue_width_limit(self):
        iq = IssueQueue(entries=16, issue_width=3)
        uops = [
            {"valid": True, "func_type": 0, "ready1": True, "ready2": True,
             "dest": i, "src1_tag": i, "src2_tag": i+1} for i in range(5)
        ]
        iq.alloc(uops)
        issued = iq.issue({"int": 3})  # default uses issue_width
        self.assertEqual(len(issued), 3)
        self.assertEqual(iq.count, 2)

    def test_eight_issue_per_cycle(self):
        iq = IssueQueue(entries=16, issue_width=8)
        uops = [
            {"valid": True, "func_type": 0, "ready1": True, "ready2": True,
             "dest": i, "src1_tag": i, "src2_tag": i+1} for i in range(10)
        ]
        iq.alloc(uops)
        issued = iq.issue({"int": 8})
        self.assertEqual(len(issued), 8)
        self.assertEqual(iq.count, 2)

    def test_128_entry_capacity(self):
        iq = IssueQueue(entries=128, issue_width=8)
        uops = []
        for i in range(32):
            uops.append({"valid": True, "func_type": 0, "ready1": True, "ready2": True, "dest": i})
        for i in range(32):
            uops.append({"valid": True, "func_type": 1, "ready1": True, "ready2": True, "dest": 32+i})
        for i in range(32):
            uops.append({"valid": True, "func_type": 2, "ready1": True, "ready2": True, "dest": 64+i})
        for i in range(16):
            uops.append({"valid": True, "func_type": 3, "ready1": True, "ready2": True, "dest": 96+i})
        for i in range(16):
            uops.append({"valid": True, "func_type": 4, "ready1": True, "ready2": True, "dest": 112+i})
        iq.alloc(uops)
        total = 0
        while iq.count:
            total += len(iq.issue({"int": 2, "fp": 2, "vector": 2, "mem": 2, "branch": 1}))
        self.assertEqual(total, 128)

    def test_wakeup(self):
        iq = IssueQueue(entries=8, issue_width=4)
        iq.alloc([
            {"valid": True, "func_type": 0, "dest": 1, "src1_tag": 5, "src2_tag": 6,
             "ready1": False, "ready2": True},
        ])
        self.assertEqual(len(iq.issue({"int": 1})), 0)
        iq.wakeup(5, 0x55)
        issued = iq.issue({"int": 1})
        self.assertEqual(len(issued), 1)
        self.assertEqual(issued[0]["op1"], 0x55)

    def test_fu_limits(self):
        iq = IssueQueue(entries=16, issue_width=8)
        iq.alloc([
            {"valid": True, "func_type": 4, "ready1": True, "ready2": True,
             "dest": 1, "src1_tag": 1, "src2_tag": 2},
            {"valid": True, "func_type": 4, "ready1": True, "ready2": True,
             "dest": 2, "src1_tag": 3, "src2_tag": 4},
        ])
        issued = iq.issue({"branch": 1})
        self.assertEqual(len(issued), 1)

    def test_flush(self):
        iq = IssueQueue(entries=16, issue_width=4)
        iq.alloc([
            {"valid": True, "func_type": 0, "ready1": True, "ready2": True, "dest": 1},
            {"valid": True, "func_type": 0, "ready1": True, "ready2": True, "dest": 2},
        ])
        iq.flush()
        self.assertEqual(iq.count, 0)
        issued = iq.issue({"int": 2})
        self.assertEqual(len(issued), 0)

    def test_pred_mask_passthrough(self):
        iq = IssueQueue(entries=4, issue_width=2)
        iq.alloc([
            {"valid": True, "func_type": 2, "ready1": True, "ready2": True,
             "ready3": True, "pred_mask": 0xAA, "dest": 1}
        ])
        issued = iq.issue({"vector": 1})
        self.assertEqual(len(issued), 1)
        self.assertEqual(issued[0]["pred_mask"], 0xAA)

if __name__ == '__main__':
    unittest.main()
