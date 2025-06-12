class VectorLSU:
    """Simplified vector LSU model supporting gather/scatter accesses."""

    def __init__(self, memory=None):
        from tb.uvm_components.data_memory_model import DataMemoryModel
        self.mem = memory if memory is not None else DataMemoryModel()

    def scatter(self, base, indices, scale, data):
        """Store a 512‑bit vector using gather/scatter addressing.

        ``scale`` is the log2 of the element size in bytes.
        """
        step = 1 << scale
        for i in range(8):
            addr = base + indices[i] * step
            lane = (data >> (i * 64)) & 0xFFFFFFFFFFFFFFFF
            self.mem.store(addr, lane)

    def gather(self, base, indices, scale):
        """Load a 512‑bit vector using gather/scatter addressing."""
        step = 1 << scale
        result = 0
        for i in range(8):
            addr = base + indices[i] * step
            lane = self.mem.load(addr)
            result |= (lane & 0xFFFFFFFFFFFFFFFF) << (i * 64)
        return result

    def store(self, base, data):
        self.scatter(base, list(range(8)), 3, data)

    def load(self, base):
        return self.gather(base, list(range(8)), 3)
