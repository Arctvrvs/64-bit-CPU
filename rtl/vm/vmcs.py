class VMCS:
    """Minimal VM control structure model."""
    def __init__(self):
        self.vmid = 0
        self.running = False

    def vm_on(self, vmid: int):
        self.vmid = vmid & 0xFF
        self.running = True

    def vm_off(self):
        self.running = False

    def current_vmid(self):
        return self.vmid if self.running else None
