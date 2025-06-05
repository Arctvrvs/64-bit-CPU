from rtl.core_tile_2smts_8wide import CoreTile2SMT8Wide

class RiscvSoC4Core:
    """Placeholder SoC model with four cores."""
    def __init__(self):
        self.cores = [CoreTile2SMT8Wide(i) for i in range(4)]
        self.cycles = 0

    def step(self):
        self.cycles += 1
        for c in self.cores:
            c.step()
