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


if __name__ == "__main__":
    unittest.main()
