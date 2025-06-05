class PageWalker8:
    """Simple page walker model that maps virtual addresses to physical addresses.
    A dictionary is used for all entries and lookups complete immediately."""

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
