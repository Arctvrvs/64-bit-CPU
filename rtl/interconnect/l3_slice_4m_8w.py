class L3Slice:
    """Simple dictionary-backed cache slice."""

    def __init__(self):
        self.mem = {}

    def read(self, addr):
        return self.mem.get(addr, 0)

    def write(self, addr, data):
        self.mem[addr] = data
