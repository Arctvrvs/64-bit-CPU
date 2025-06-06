class PageWalker8:
    """Simple page walker model that maps virtual addresses to physical addresses.
    A dictionary is used for all entries and lookups complete immediately."""

    def __init__(self, *, coverage=None):
        self.table = {}
        self.coverage = coverage

    def set_entry(self, va, pa, perm='rw'):
        self.table[va] = (pa, perm)

    def walk(self, va, perm='r'):
        if va not in self.table:
            fault = True
            pa = 0
        else:
            pa, permissions = self.table[va]
            fault = perm not in permissions
        if self.coverage:
            self.coverage.record_page_walk(fault)
        return pa, fault
