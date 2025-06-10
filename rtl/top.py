from rtl.riscv_soc_4core import RiscvSoC4Core

class Top:
    """Simulation helper that wraps :class:`RiscvSoC4Core`."""

    def __init__(self):
        self.soc = RiscvSoC4Core()
        self.cycles = 0

    def step(self):
        """Advance the SoC simulation by one cycle."""
        self.cycles += 1
        self.soc.step()
