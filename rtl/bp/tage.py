class TAGEPredictor:
    """Simplified TAGE branch predictor model."""
    def __init__(self, tables=5, entries=1024):
        self.tables = tables
        self.entries = entries
        self.mask = entries - 1
        # Initialize 2-bit counters to weakly not taken (1)
        self.table = [[1 for _ in range(entries)] for _ in range(tables)]
        self.history = 0
        self.hist_mask = (1 << tables) - 1

    def _index(self, pc, t):
        return (pc ^ (self.history >> t)) & self.mask

    def predict(self, pc):
        score = 0
        for t in range(self.tables):
            idx = self._index(pc, t)
            score += self.table[t][idx] >> 1  # high bit
        return score > self.tables // 2

    def update(self, pc, taken):
        for t in range(self.tables):
            idx = self._index(pc, t)
            if taken:
                if self.table[t][idx] < 3:
                    self.table[t][idx] += 1
            else:
                if self.table[t][idx] > 0:
                    self.table[t][idx] -= 1
        self.history = ((self.history << 1) | int(bool(taken))) & self.hist_mask
