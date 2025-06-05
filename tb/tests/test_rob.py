import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.rob_rs_iq.rob import ROB

class ROBTest(unittest.TestCase):
    def test_alloc_writeback_commit(self):
        rob = ROB(entries=8)
        idxs = rob.alloc([
            {'dest': 5, 'old': 1},
            {'dest': 6, 'old': 2},
        ])
        rob.writeback(idxs[1])
        self.assertIsNone(rob.commit())
        rob.writeback(idxs[0])
        entry1 = rob.commit()
        entry2 = rob.commit()
        self.assertEqual(entry1['dest'], 5)
        self.assertEqual(entry2['dest'], 6)
        self.assertIsNone(rob.commit())

if __name__ == '__main__':
    unittest.main()
