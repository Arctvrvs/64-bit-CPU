class CoverageModel:
    """Collects simple functional coverage statistics."""
    def __init__(self):
        self.opcodes = set()
        self.btb_events = set()
        self.cache_hits = {"L1": 0, "L2": 0, "L3": 0}
        self.cache_misses = {"L1": 0, "L2": 0, "L3": 0}
        self.tlb_hits = {"L1": 0, "L2": 0}
        self.tlb_misses = {"L1": 0, "L2": 0}
        self.exceptions = {}
        self.branches = 0
        self.mispredicts = 0

    def reset(self):
        """Clear all collected coverage statistics."""
        self.opcodes.clear()
        self.btb_events.clear()
        for lvl in self.cache_hits:
            self.cache_hits[lvl] = 0
            self.cache_misses[lvl] = 0
        for lvl in self.tlb_hits:
            self.tlb_hits[lvl] = 0
            self.tlb_misses[lvl] = 0
        self.exceptions.clear()
        self.branches = 0
        self.mispredicts = 0

    def record_opcode(self, opcode: int):
        """Record execution of an opcode (7-bit value)."""
        self.opcodes.add(opcode & 0x7F)

    def record_btb_event(self, index: int, tag: int):
        """Record a branch predictor allocation event."""
        self.btb_events.add((index, tag))

    def record_cache(self, level: str, hit: bool):
        """Record a cache hit or miss for *level* ('L1','L2','L3')."""
        if hit:
            self.cache_hits[level] += 1
        else:
            self.cache_misses[level] += 1

    def record_tlb(self, level: str, hit: bool):
        """Record a TLB hit or miss for *level* ('L1','L2')."""
        if hit:
            self.tlb_hits[level] += 1
        else:
            self.tlb_misses[level] += 1

    def record_exception(self, exc: str):
        """Record an exception code such as 'illegal' or 'page'."""
        self.exceptions[exc] = self.exceptions.get(exc, 0) + 1

    def record_branch(self, mispredict: bool):
        """Record a branch outcome and whether it was mispredicted."""
        self.branches += 1
        if mispredict:
            self.mispredicts += 1

    def opcode_coverage(self):
        """Return the set of unique opcodes seen."""
        return set(self.opcodes)

    def summary(self):
        """Return a dictionary summarizing collected coverage."""
        return {
            "opcodes": len(self.opcodes),
            "btb_entries": len(self.btb_events),
            "cache_hits": dict(self.cache_hits),
            "cache_misses": dict(self.cache_misses),
            "tlb_hits": dict(self.tlb_hits),
            "tlb_misses": dict(self.tlb_misses),
            "exceptions": dict(self.exceptions),
            "branches": self.branches,
            "mispredicts": self.mispredicts,
        }
