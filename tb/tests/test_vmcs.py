import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.vm.vmcs import VMCS

class VMCSTest(unittest.TestCase):
    def test_on_off(self):
        vm = VMCS()
        vm.vm_on(3)
        self.assertTrue(vm.running)
        self.assertEqual(vm.current_vmid(), 3)
        vm.vm_off()
        self.assertFalse(vm.running)
        self.assertIsNone(vm.current_vmid())

if __name__ == '__main__':
    unittest.main()
