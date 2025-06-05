class CsrFile:
    """Minimal CSR file model tracking cycle and instret counters."""
    def __init__(self, num_csrs=32):
        self.csrs = {i: 0 for i in range(num_csrs)}
        self.cycles = 0
        self.instret = 0

    def write(self, addr, data):
        if addr in self.csrs:
            self.csrs[addr] = data & 0xFFFFFFFFFFFFFFFF

    def read(self, addr):
        if addr == 0xC00:
            return self.cycles
        if addr == 0xC02:
            return self.instret
        return self.csrs.get(addr, 0)

    def step(self, instret_inc=0):
        self.cycles += 1
        self.instret += instret_inc
