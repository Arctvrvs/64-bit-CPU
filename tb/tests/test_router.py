import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.interconnect.router_5port import Router5Port

class RouterTest(unittest.TestCase):
    def test_route(self):
        r = Router5Port()
        pkt = {'north':1, 'south':2, 'east':3, 'west':4, 'local':5}
        self.assertEqual(r.route(pkt), pkt)

if __name__ == '__main__':
    unittest.main()
