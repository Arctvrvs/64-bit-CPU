class BTB:
    """Simple Branch Target Buffer model with dictionary lookup"""
    def __init__(self, entries=8):
        self.entries = entries
        self.table = {}

    def predict(self, pc):
        if pc in self.table:
            return True, self.table[pc]
        return False, pc + 4

    def update(self, pc, target, taken):
        if taken:
            if len(self.table) >= self.entries:
                # remove oldest entry
                self.table.pop(next(iter(self.table)))
            self.table[pc] = target
        elif pc in self.table:
            self.table[pc] = target
