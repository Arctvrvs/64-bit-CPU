class L2Cache:
    """Simple dictionary-based L2 cache model."""
    def __init__(self):
        self.mem = {}

    def read(self, addr):
        return self.mem.get(addr, 0)

    def write(self, addr, data):
        self.mem[addr] = data
