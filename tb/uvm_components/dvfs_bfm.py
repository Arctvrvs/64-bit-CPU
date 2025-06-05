class DVFSBFM:
    """Variable-frequency clock generator for simulation tests."""

    def __init__(self, period=2):
        self.period = period
        self.counter = 0
        self.clk = 0

    def tick(self):
        """Advance one simulation step and update the clock value."""
        self.counter += 1
        if self.counter >= self.period:
            self.counter = 0
            self.clk ^= 1
        return self.clk

    def set_period(self, period):
        """Change the clock period on the fly."""
        self.period = max(1, int(period))

    def get(self):
        """Return the current clock level."""
        return self.clk
