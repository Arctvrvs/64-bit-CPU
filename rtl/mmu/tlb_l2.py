class TlbL2:
    """Simple associative L2 TLB with fixed number of entries and latency."""

    def __init__(self, entries=4, *, hit_latency=8, miss_latency=20, coverage=None):
        self.entries = entries
        self.table = {}
        self.hit_latency = hit_latency
        self.miss_latency = miss_latency
        self.coverage = coverage
        self.last_latency = 0

    def lookup(self, va, perm='r'):
        if va in self.table:
            pa, permissions = self.table[va]
            fault = perm not in permissions
            hit = True
        else:
            pa = 0
            permissions = ''
            fault = False
            hit = False

        self.last_latency = self.hit_latency if hit else self.miss_latency
        if self.coverage:
            self.coverage.record_tlb('L2', hit)
            self.coverage.record_tlb_latency('L2', self.last_latency)
            if fault:
                self.coverage.record_tlb_fault('L2')

        if hit:
            return True, pa, fault
        return False, 0, False

    def refill(self, va, pa, perm='rw'):
        if len(self.table) >= self.entries:
            self.table.pop(next(iter(self.table)))
        self.table[va] = (pa, perm)
