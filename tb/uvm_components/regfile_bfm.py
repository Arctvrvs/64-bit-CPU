class RegFileBFM:
    """Register file bus functional model checking writes against the golden model."""

    def __init__(self, start_pc=0):
        from rtl.isa.golden_model import GoldenModel
        self.gm = GoldenModel(pc=start_pc)

    def reset(self, pc=0):
        """Reset the internal golden model."""
        from rtl.isa.golden_model import GoldenModel
        self.gm = GoldenModel(pc=pc)

    def write(self, instr, rd_arch, rd_val):
        """Execute *instr* and compare the RD value with the golden model."""
        self.gm.step(instr)
        return self.gm.regs[rd_arch] == rd_val
