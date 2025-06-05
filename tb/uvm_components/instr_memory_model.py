class InstructionMemoryModel:
    """Simple instruction memory backed by a DRAMModel."""

    def __init__(self, dram=None):
        from rtl.interconnect.dram_model import DRAMModel
        self.dram = dram if dram is not None else DRAMModel()

    def load_program(self, addr, instructions):
        """Load a list of 32-bit instructions starting at *addr*."""
        for i, instr in enumerate(instructions):
            self.dram.write(addr + 4 * i, instr & 0xFFFFFFFF)

    def fetch(self, addr):
        """Return the 32-bit instruction stored at *addr* or 0."""
        return self.dram.read(addr) & 0xFFFFFFFF
