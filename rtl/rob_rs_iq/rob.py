class ROB:
    """Simple reorder buffer model."""
    def __init__(self, entries=256):
        self.entries = [None] * entries
        self.entries_ready = [False] * entries
        self.branch_misp = [False] * entries
        self.branch_target = [0] * entries
        self.head = 0
        self.tail = 0
        self.count = 0
        self.size = entries

    def alloc(self, uops):
        """Allocate a list of uops. Each uop is dict with keys 'dest' and 'old'."""
        idxs = []
        for u in uops:
            if self.count >= self.size:
                idxs.append(None)
                continue
            self.entries[self.tail] = dict(u)
            self.entries_ready[self.tail] = False
            idxs.append(self.tail)
            self.tail = (self.tail + 1) % self.size
            self.count += 1
        return idxs

    def writeback(self, idx, mispredict=False, target=0):
        if idx is not None:
            self.entries_ready[idx] = True
            self.branch_misp[idx] = mispredict
            self.branch_target[idx] = target

    def commit(self):
        if self.count == 0:
            return None
        if self.entries[self.head] is not None and self.entries_ready[self.head]:
            entry = self.entries[self.head]
            entry['mispredict'] = self.branch_misp[self.head]
            entry['target'] = self.branch_target[self.head]
            self.entries[self.head] = None
            self.entries_ready[self.head] = False
            self.branch_misp[self.head] = False
            self.branch_target[self.head] = 0
            self.head = (self.head + 1) % self.size
            self.count -= 1
            return entry
        return None
