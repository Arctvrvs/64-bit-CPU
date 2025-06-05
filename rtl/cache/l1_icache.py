class L1ICache:
    """Simple in-memory model of the L1 instruction cache."""
    def __init__(self):
        self.mem = {}

    def load(self, addr, data):
        """Load a 32-bit instruction word at the given address."""
        self.mem[addr & ~0x3] = data & 0xFFFFFFFF

    def fetch(self, addr):
        """Return the instruction word stored at the address or 0."""
        return self.mem.get(addr & ~0x3, 0)
