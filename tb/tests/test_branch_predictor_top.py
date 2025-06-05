import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.bp.branch_predictor_top import BranchPredictorTop


class BranchPredictorTopTest(unittest.TestCase):
    def test_call_and_return(self):
        bp = BranchPredictorTop(entries=4)
        # predict call, push return address
        taken, tgt = bp.predict(0x100, is_call=True, is_uncond_branch=True)
        self.assertTrue(taken)
        # update with actual target
        bp.update(0x100, True, 0x200, is_branch=True)
        # predict return should use RSB
        taken, tgt = bp.predict(0x200, is_ret=True)
        self.assertTrue(taken)
        self.assertEqual(tgt, 0x104)
        bp.update(0x200, True, 0x104, is_branch=True, is_ret=True)

    def test_conditional_branch(self):
        bp = BranchPredictorTop()
        bp.update(0x300, True, 0x320, is_branch=True)
        taken, tgt = bp.predict(0x300, is_cond_branch=True)
        self.assertTrue(taken)
        self.assertEqual(tgt, 0x320)

    def test_indirect_branch(self):
        bp = BranchPredictorTop()
        bp.update(0x400, True, 0x500, is_indirect=True)
        taken, tgt = bp.predict(0x400, is_indirect=True, last_target=0)
        self.assertTrue(taken)
        self.assertEqual(tgt, 0x500)


if __name__ == '__main__':
    unittest.main()
