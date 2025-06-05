class PageWalker:
    """Simplified page walker that resolves a VA using an internal page table."""
    def __init__(self):
        self.table = {}

    def set_entry(self, va, pa, perm='rw'):
        self.table[va] = (pa, perm)

    def walk(self, va, perm='r'):
        if va not in self.table:
            return 0, True
        pa, permissions = self.table[va]
        fault = perm not in permissions
        return pa, fault
