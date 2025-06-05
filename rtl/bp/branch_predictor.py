class BranchPredictor:
    """Simple branch predictor model with a tiny BTB."""

    def __init__(self, entries=32):
        self.entries = entries
        self.index_mask = entries - 1
        self.index_bits = entries.bit_length() - 1
        self.tag_shift = self.index_bits + 2
        self.table = [
            {"tag": 0, "target": 0, "ctr": 1} for _ in range(entries)
        ]

    def predict(self, pc):
        idx = (pc >> 2) & self.index_mask
        entry = self.table[idx]
        if entry["tag"] == (pc >> self.tag_shift):
            taken = entry["ctr"] >> 1
            target = entry["target"]
        else:
            taken = 0
            target = (pc + 4) & 0xFFFFFFFFFFFFFFFF
        return taken, target

    def update(self, pc, taken, target):
        idx = (pc >> 2) & self.index_mask
        entry = self.table[idx]
        entry["tag"] = pc >> self.tag_shift
        entry["target"] = target & 0xFFFFFFFFFFFFFFFF
        if taken:
            if entry["ctr"] < 3:
                entry["ctr"] += 1
        else:
            if entry["ctr"] > 0:
                entry["ctr"] -= 1

