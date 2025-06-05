class VectorLSU:
    """Simplified vector LSU model issuing sequential lane accesses."""
    def __init__(self, memory=None):
        from tb.uvm_components.data_memory_model import DataMemoryModel
        self.mem = memory if memory is not None else DataMemoryModel()

    def store(self, base, data):
        for i in range(8):
            self.mem.store(base + i*8, (data >> (i*64)) & 0xFFFFFFFFFFFFFFFF)

    def load(self, base):
        result = 0
        for i in range(8):
            lane = self.mem.load(base + i*8)
            result |= (lane & 0xFFFFFFFFFFFFFFFF) << (i*64)
        return result
