import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tb.uvm_components.coverage import CoverageModel


class CoverageModelTest(unittest.TestCase):
    def test_collect(self):
        cov = CoverageModel()
        cov.record_opcode(0x33)
        cov.record_opcode(0x13)
        cov.record_opcode(0x33)  # duplicate
        cov.record_btb_event(1, 0x55)
        cov.record_btb_event(1, 0x55)
        cov.record_cache('L1', True)
        cov.record_cache('L1', False)
        cov.record_tlb('L1', True)
        cov.record_tlb('L2', False)
        summary = cov.summary()
        self.assertEqual(summary['opcodes'], 2)
        self.assertEqual(summary['btb_entries'], 1)
        self.assertEqual(summary['cache_hits']['L1'], 1)
        self.assertEqual(summary['cache_misses']['L1'], 1)
        self.assertEqual(summary['tlb_hits']['L1'], 1)
        self.assertEqual(summary['tlb_misses']['L2'], 1)

    def test_reset(self):
        cov = CoverageModel()
        cov.record_opcode(0x33)
        cov.reset()
        self.assertEqual(cov.summary()['opcodes'], 0)

    def test_exceptions(self):
        cov = CoverageModel()
        cov.record_exception('illegal')
        cov.record_exception('illegal')
        cov.record_exception('page')
        summary = cov.summary()
        self.assertEqual(summary['exceptions']['illegal'], 2)
        self.assertEqual(summary['exceptions']['page'], 1)

    def test_branches(self):
        cov = CoverageModel()
        cov.record_branch(mispredict=False)
        cov.record_branch(mispredict=True)
        cov.record_branch(mispredict=True)
        summary = cov.summary()
        self.assertEqual(summary['branches'], 3)
        self.assertEqual(summary['mispredicts'], 2)


if __name__ == '__main__':
    unittest.main()
