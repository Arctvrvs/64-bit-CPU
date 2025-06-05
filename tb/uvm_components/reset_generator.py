class ResetGenerator:
    """Generate a simple active-low reset pulse for simulation tests."""

    def __init__(self, cycles=5):
        self.cycles = cycles
        self.cycle = 0
        self.value = 0  # rst_n signal, 0 during reset

    def tick(self):
        """Advance one cycle and update ``rst_n`` state."""
        self.cycle += 1
        self.value = 1 if self.cycle >= self.cycles else 0
        return self.value

    def get(self):
        """Return the current ``rst_n`` value."""
        return self.value

    def reset(self):
        """Restart the reset pulse generation."""
        self.cycle = 0
        self.value = 0
