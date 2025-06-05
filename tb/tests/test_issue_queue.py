import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rob_rs_iq.issue_queue import IssueQueue

class IssueQueueTest(unittest.TestCase):
    def test_basic_alloc_issue(self):
        iq = IssueQueue(entries=4)
        iq.alloc([
            {"valid": True, "op1": 1, "op2": 2, "dest": 5, "rob_idx": 0, "ready1": True, "ready2": True},
            {"valid": True, "op1": 3, "op2": 4, "dest": 6, "rob_idx": 1, "ready1": True, "ready2": True},
        ])
        issued = iq.issue(max_issue=2)
        self.assertEqual(len(issued), 2)
        self.assertEqual(issued[0]["dest"], 5)
        self.assertEqual(issued[1]["dest"], 6)
        self.assertEqual(iq.count, 0)

if __name__ == '__main__':
    unittest.main()
