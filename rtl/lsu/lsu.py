class LSU:
    """Simple load/store unit model using DataMemoryModel and MMU helpers."""

    def __init__(self, memory=None, tlb_l1=None, tlb_l2=None, walker=None, *, coverage=None):
        from tb.uvm_components.data_memory_model import DataMemoryModel
        from rtl.mmu import TlbL1, TlbL2, PageWalker8
        self.mem = memory if memory is not None else DataMemoryModel()
        self.tlb_l1 = tlb_l1 if tlb_l1 is not None else TlbL1(coverage=coverage)
        self.tlb_l2 = tlb_l2 if tlb_l2 is not None else TlbL2(coverage=coverage)
        self.walker = walker if walker is not None else PageWalker8(coverage=coverage)
        self.coverage = coverage

    def _translate(self, va, perm='r'):
        hit, pa, fault = self.tlb_l1.lookup(va, perm=perm)
        latency = self.tlb_l1.last_latency
        if hit:
            return pa, fault, latency

        hit, pa, fault = self.tlb_l2.lookup(va, perm=perm)
        latency += self.tlb_l2.last_latency
        if hit:
            self.tlb_l1.refill(va, pa, perm='rwx')
            return pa, fault, latency

        pa, fault = self.walker.walk(va, perm=perm)
        latency += 30  # approximate page walk latency
        if not fault:
            self.tlb_l2.refill(va, pa, perm='rwx')
            self.tlb_l1.refill(va, pa, perm='rwx')
        elif self.coverage:
            # attribute faults after walker to the L2 TLB level
            self.coverage.record_tlb_fault('L2')
        return pa, fault, latency

    def cycle(self, ops):
        """Process up to two operations.

        *ops* is a list of two dictionaries describing the operation or None.
        Each dictionary may contain:
            - ``is_store`` (bool)
            - ``addr`` (int)
            - ``data`` (int)
            - ``size`` (int bytes, default 8)
            - ``dest`` (int) destination register for loads
            - ``rob`` (int) ROB index for bookkeeping
        Returns a list of two result dictionaries for load operations.
        """
        results = [None, None]
        for idx, op in enumerate(ops):
            if not op:
                continue
            size = op.get("size", 8)
            va = op.get("addr", 0)
            perm = 'w' if op.get("is_store", False) else 'r'
            pa, fault, lat = self._translate(va, perm=perm)
            if fault:
                results[idx] = {"fault": True, "rob": op.get("rob"), "latency": lat}
                continue
            if op.get("is_store", False):
                self.mem.store(pa, op.get("data", 0), size=size)
            else:
                data = self.mem.load(pa, size=size)
                results[idx] = {
                    "data": data,
                    "dest": op.get("dest"),
                    "rob": op.get("rob"),
                    "latency": lat,
                }
        return results
