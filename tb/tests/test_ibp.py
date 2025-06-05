import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.bp.ibp import IBPPredictor

class IBPPredictorTest(unittest.TestCase):
    def test_basic_predict_update(self):
        ibp = IBPPredictor(entries=8)
        pc = 0x80
        last = 0x20
        self.assertEqual(ibp.predict(pc, last), 0)
        ibp.update(pc, last, 0x1234)
        self.assertEqual(ibp.predict(pc, last), 0x1234)
        # Different last target should not hit
        self.assertEqual(ibp.predict(pc, last + 4), 0)

if __name__ == '__main__':
    unittest.main()
