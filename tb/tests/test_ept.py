import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.vm.ept import EPT

class EPTTest(unittest.TestCase):
    def test_translate(self):
        ept = EPT(key=0xdeadbeef)
        gpa = 0x1000
        vmid = 2
        expect = (gpa ^ (0xdeadbeef ^ (vmid * 0x1000))) & 0xFFFFFFFFFFFFFFFF
        self.assertEqual(ept.translate(vmid, gpa), expect)

if __name__ == '__main__':
    unittest.main()
