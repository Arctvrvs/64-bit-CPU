class ArchRegFile:
    """Simple architectural register file model."""
    def __init__(self):
        self.regs = [0] * 32

    def write(self, idx, data):
        if idx != 0:
            self.regs[idx] = data & 0xFFFFFFFFFFFFFFFF

    def read(self, idx):
        if idx == 0:
            return 0
        return self.regs[idx]
