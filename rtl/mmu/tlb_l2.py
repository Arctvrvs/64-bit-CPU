class TlbL2:
    """Simple associative L2 TLB with fixed number of entries."""
    def __init__(self, entries=4):
        self.entries = entries
        self.table = {}

    def lookup(self, va, perm='r'):
        if va in self.table:
            pa, permissions = self.table[va]
            fault = perm not in permissions
            return True, pa, fault
        return False, 0, False

    def refill(self, va, pa, perm='rw'):
        if len(self.table) >= self.entries:
            self.table.pop(next(iter(self.table)))
        self.table[va] = (pa, perm)
