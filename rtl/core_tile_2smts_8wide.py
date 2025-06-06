class CoreTile2SMT8Wide:
    """Placeholder dual-SMT core tile model."""
    def __init__(self, core_id=0):
        self.core_id = core_id
        self.cycles = 0

    def step(self):
        self.cycles += 1
