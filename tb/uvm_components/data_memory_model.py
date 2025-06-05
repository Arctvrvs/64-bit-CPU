class DataMemoryModel:
    """Simple data memory backed by a DRAMModel."""

    def __init__(self, dram=None):
        from rtl.interconnect.dram_model import DRAMModel
        self.dram = dram if dram is not None else DRAMModel()

    def store(self, addr, data, size=8):
        """Store *size* bytes of *data* at *addr*."""
        mask = (1 << (size * 8)) - 1
        self.dram.write(addr, data & mask)

    def load(self, addr, size=8):
        """Load *size* bytes from *addr* and return the value."""
        mask = (1 << (size * 8)) - 1
        return self.dram.read(addr) & mask
