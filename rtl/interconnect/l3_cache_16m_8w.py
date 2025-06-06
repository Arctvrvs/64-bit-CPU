class L3Cache16M8W:
    """Very small model of a shared L3 cache implemented as a dictionary with
    optional coverage."""

    def __init__(self, *, coverage=None):
        self.mem = {}
        self.coverage = coverage

    def read(self, addr):
        hit = addr in self.mem
        val = self.mem.get(addr, 0)
        if self.coverage:
            self.coverage.record_cache('L3', hit)
        return val

    def write(self, addr, data):
        hit = addr in self.mem
        self.mem[addr] = data
        if self.coverage:
            self.coverage.record_cache('L3', hit)
