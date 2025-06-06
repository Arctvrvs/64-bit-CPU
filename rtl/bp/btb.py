class BTB:
    """Simple Branch Target Buffer model with optional coverage hooks."""

    def __init__(self, entries=8, *, coverage=None):
        self.entries = entries
        self.table = {}
        self.coverage = coverage

    def predict(self, pc):
        if pc in self.table:
            return True, self.table[pc]
        return False, pc + 4

    def update(self, pc, target, taken):
        if taken:
            if len(self.table) >= self.entries:
                self.table.pop(next(iter(self.table)))
            self.table[pc] = target
            if self.coverage:
                index = pc % self.entries
                tag = pc >> 2
                self.coverage.record_btb_event(index, tag)
        elif pc in self.table:
            self.table[pc] = target
