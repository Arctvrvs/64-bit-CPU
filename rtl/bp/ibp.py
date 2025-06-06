class IBPPredictor:
    """Simple indirect branch predictor using a hash of PC and last target."""

    def __init__(self, entries=512, *, coverage=None):
        self.entries = entries
        self.mask = entries - 1
        self.table = {}
        self.coverage = coverage

    def _index(self, pc, last):
        return (pc ^ last) & self.mask

    def predict(self, pc, last):
        idx = self._index(pc, last)
        entry = self.table.get(idx)
        if entry and entry[0] == pc:
            return entry[1]
        return 0

    def update(self, pc, last, target):
        idx = self._index(pc, last)
        new_tag = pc
        if self.table.get(idx) != (pc, target & 0xFFFFFFFFFFFFFFFF) and self.coverage:
            self.coverage.record_ibp_event(idx, new_tag >> 2)
        self.table[idx] = (pc, target & 0xFFFFFFFFFFFFFFFF)
