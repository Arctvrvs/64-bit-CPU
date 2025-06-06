import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rtl.interconnect.interconnect_mesh_2x2 import InterconnectMesh2x2

class InterconnectMeshTest(unittest.TestCase):
    def test_simple_route(self):
        mesh = InterconnectMesh2x2()
        mesh.send(0, 3, 'hello')
        outputs = mesh.step()
        self.assertEqual(outputs[3], [{'src': 0, 'data': 'hello'}])
        # no other destinations should have data
        self.assertEqual(outputs[0], [])
        self.assertEqual(outputs[1], [])
        self.assertEqual(outputs[2], [])

if __name__ == '__main__':
    unittest.main()

