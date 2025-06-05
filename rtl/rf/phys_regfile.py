class PhysRegFile:
    """Simple physical register file model."""
    def __init__(self, entries=128):
        self.regs = [0] * entries

    def write(self, idx, data):
        self.regs[idx] = data & 0xFFFFFFFFFFFFFFFF

    def read(self, idx):
        return self.regs[idx]
