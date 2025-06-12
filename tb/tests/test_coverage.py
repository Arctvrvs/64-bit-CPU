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
        cov.record_tlb_fault('L1')
        cov.record_tlb_fault('L2')
        cov.record_tlb_latency('L1', 2)
        cov.record_tlb_latency('L2', 5)
        cov.record_immediate(0x10)
        cov.record_immediate(0x20)
        summary = cov.summary()
        self.assertEqual(summary['opcodes'], 2)
        self.assertEqual(summary['btb_entries'], 1)
        self.assertEqual(summary['cache_hits']['L1'], 1)
        self.assertEqual(summary['cache_misses']['L1'], 1)
        self.assertEqual(summary['tlb_hits']['L1'], 1)
        self.assertEqual(summary['tlb_misses']['L2'], 1)
        self.assertEqual(summary['tlb_faults']['L1'], 1)
        self.assertEqual(summary['tlb_faults']['L2'], 1)
        self.assertEqual(summary['tlb_latency']['L1'], [2])
        self.assertEqual(summary['tlb_latency']['L2'], [5])
        self.assertEqual(summary['immediates'], 2)

    def test_reset(self):
        cov = CoverageModel()
        cov.record_opcode(0x33)
        cov.record_tlb_latency('L1', 4)
        cov.record_immediate(0x5)
        cov.reset()
        self.assertEqual(cov.summary()['opcodes'], 0)
        self.assertEqual(cov.summary()['tlb_latency']['L1'], [])
        self.assertEqual(cov.summary()['immediates'], 0)

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

    def test_page_walks(self):
        cov = CoverageModel()
        cov.record_page_walk(False)
        cov.record_page_walk(True)
        cov.record_page_walk(True)
        summary = cov.summary()
        self.assertEqual(summary['page_walks'], 3)
        self.assertEqual(summary['page_walk_faults'], 2)

    def test_save_and_load_summary(self):
        cov = CoverageModel()
        cov.record_opcode(0x33)
        path = os.path.join(os.path.dirname(__file__), 'cov_tmp.json')
        cov.save_summary(path)
        loaded = CoverageModel.load_summary(path)
        os.remove(path)
        self.assertEqual(loaded['opcodes'], 1)

    def test_merge(self):
        cov1 = CoverageModel()
        cov2 = CoverageModel()
        cov1.record_opcode(0x33)
        cov2.record_opcode(0x13)
        cov2.record_branch(mispredict=True)
        cov1.merge(cov2)
        summary = cov1.summary()
        self.assertEqual(summary['opcodes'], 2)
        self.assertEqual(summary['branches'], 1)
        self.assertEqual(summary['mispredicts'], 1)


if __name__ == '__main__':
    unittest.main()
