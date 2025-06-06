class CoverageModel:
    """Collects simple functional coverage statistics."""
    def __init__(self):
        self.opcodes = set()
        self.btb_events = set()
        self.tage_events = {}
        self.ibp_events = set()
        self.cache_hits = {"L1": 0, "L2": 0, "L3": 0}
        self.cache_misses = {"L1": 0, "L2": 0, "L3": 0}
        self.tlb_hits = {"L1": 0, "L2": 0}
        self.tlb_misses = {"L1": 0, "L2": 0}
        self.tlb_faults = {"L1": 0, "L2": 0}
        # store a list of observed lookup latencies per TLB level
        self.tlb_latency = {"L1": [], "L2": []}
        self.immediates = set()
        self.rsb_underflow = 0
        self.rsb_overflow = 0
        self.exceptions = {}
        self.branches = 0
        self.mispredicts = 0
        self.page_walks = 0
        self.page_walk_faults = 0

    def reset(self):
        """Clear all collected coverage statistics."""
        self.opcodes.clear()
        self.btb_events.clear()
        self.tage_events.clear()
        self.ibp_events.clear()
        for lvl in self.cache_hits:
            self.cache_hits[lvl] = 0
            self.cache_misses[lvl] = 0
        for lvl in self.tlb_hits:
            self.tlb_hits[lvl] = 0
            self.tlb_misses[lvl] = 0
            self.tlb_faults[lvl] = 0
            self.tlb_latency[lvl].clear()
        self.exceptions.clear()
        self.immediates.clear()
        self.rsb_underflow = 0
        self.rsb_overflow = 0
        self.branches = 0
        self.mispredicts = 0
        self.page_walks = 0
        self.page_walk_faults = 0

    def record_opcode(self, opcode: int):
        """Record execution of an opcode (7-bit value)."""
        self.opcodes.add(opcode & 0x7F)

    def record_btb_event(self, index: int, tag: int):
        """Record a branch predictor allocation event."""
        self.btb_events.add((index, tag))

    def record_tage_event(self, table: int, index: int, tag: int):
        """Record a TAGE predictor allocation event."""
        if table not in self.tage_events:
            self.tage_events[table] = set()
        self.tage_events[table].add((index, tag))

    def record_ibp_event(self, index: int, tag: int):
        """Record an indirect branch predictor allocation."""
        self.ibp_events.add((index, tag))

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

    def record_tlb_latency(self, level: str, cycles: int):
        """Record the observed lookup latency for *level* ('L1','L2')."""
        self.tlb_latency[level].append(int(cycles))

    def record_tlb_fault(self, level: str):
        """Record a TLB permission fault for *level* ('L1','L2')."""
        self.tlb_faults[level] += 1

    def record_immediate(self, imm: int):
        """Record an immediate value used by an instruction."""
        self.immediates.add(imm & 0xFFFFFFFFFFFFFFFF)

    def record_rsb_underflow(self):
        """Record an RSB underflow event."""
        self.rsb_underflow += 1

    def record_rsb_overflow(self):
        """Record an RSB overflow event."""
        self.rsb_overflow += 1

    def record_exception(self, exc: str):
        """Record an exception code such as 'illegal' or 'page'."""
        self.exceptions[exc] = self.exceptions.get(exc, 0) + 1

    def record_branch(self, mispredict: bool):
        """Record a branch outcome and whether it was mispredicted."""
        self.branches += 1
        if mispredict:
            self.mispredicts += 1

    def record_page_walk(self, fault: bool):
        """Record that a page walk occurred and whether it faulted."""
        self.page_walks += 1
        if fault:
            self.page_walk_faults += 1

    def opcode_coverage(self):
        """Return the set of unique opcodes seen."""
        return set(self.opcodes)

    def summary(self):
        """Return a dictionary summarizing collected coverage."""
        return {
            "opcodes": len(self.opcodes),
            "btb_entries": len(self.btb_events),
            "tage_entries": {t: len(e) for t, e in self.tage_events.items()},
            "ibp_entries": len(self.ibp_events),
            "cache_hits": dict(self.cache_hits),
            "cache_misses": dict(self.cache_misses),
            "tlb_hits": dict(self.tlb_hits),
            "tlb_misses": dict(self.tlb_misses),
            "tlb_faults": dict(self.tlb_faults),
            "tlb_latency": {lvl: list(self.tlb_latency[lvl]) for lvl in self.tlb_latency},
            "immediates": len(self.immediates),
            "rsb_underflow": self.rsb_underflow,
            "rsb_overflow": self.rsb_overflow,
            "exceptions": dict(self.exceptions),
            "branches": self.branches,
            "mispredicts": self.mispredicts,
            "page_walks": self.page_walks,
            "page_walk_faults": self.page_walk_faults,
        }
