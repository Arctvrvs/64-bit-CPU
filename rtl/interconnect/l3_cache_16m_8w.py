class L3Cache16M8W:
    """Very small model of a shared L3 cache implemented as a dictionary."""

    def __init__(self):
        self.mem = {}

    def read(self, addr):
        return self.mem.get(addr, 0)

    def write(self, addr, data):
        self.mem[addr] = data
