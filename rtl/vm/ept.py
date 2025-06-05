class EPT:
    """Very small EPT model that XORs addresses with a per-VM key."""
    def __init__(self, key=0):
        self.key = key & 0xFFFFFFFFFFFFFFFF

    def translate(self, vmid: int, gpa: int) -> int:
        vm_key = (self.key ^ (vmid & 0xFF) * 0x1000) & 0xFFFFFFFFFFFFFFFF
        return (gpa ^ vm_key) & 0xFFFFFFFFFFFFFFFF
