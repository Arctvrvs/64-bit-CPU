class IssueQueue:
    """Simplified issue queue model supporting up to two issues per cycle."""
    def __init__(self, entries=16):
        self.entries = [None] * entries
        self.head = 0
        self.tail = 0
        self.count = 0
        self.size = entries

    def alloc(self, uops):
        """Allocate a list of uops in order. Each uop is a dict with keys
        'op1','op2','dest','rob_idx','ready1','ready2'."""
        for u in uops:
            if self.count >= self.size:
                break
            if not u.get('valid', True):
                continue
            self.entries[self.tail] = dict(u)
            self.tail = (self.tail + 1) % self.size
            self.count += 1

    def issue(self, max_issue=2):
        """Return up to max_issue ready uops."""
        issued = []
        while len(issued) < max_issue and self.count > 0:
            entry = self.entries[self.head]
            if entry and entry.get('ready1', True) and entry.get('ready2', True):
                issued.append(entry)
                self.entries[self.head] = None
                self.head = (self.head + 1) % self.size
                self.count -= 1
            else:
                break
        return issued
