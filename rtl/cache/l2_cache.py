class L2Cache:
    """Simple dictionary-based L2 cache model with optional coverage."""

    def __init__(self, *, coverage=None):
        self.mem = {}
        self.coverage = coverage

    def read(self, addr):
        hit = addr in self.mem
        val = self.mem.get(addr, 0)
        if self.coverage:
            self.coverage.record_cache('L2', hit)
        return val

    def write(self, addr, data):
        hit = addr in self.mem
        self.mem[addr] = data
        if self.coverage:
            self.coverage.record_cache('L2', hit)
