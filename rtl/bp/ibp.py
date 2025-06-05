class IBPPredictor:
    """Simple indirect branch predictor using a hash of PC and last target."""
    def __init__(self, entries=512):
        self.entries = entries
        self.mask = entries - 1
        self.table = {}

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
        self.table[idx] = (pc, target & 0xFFFFFFFFFFFFFFFF)
