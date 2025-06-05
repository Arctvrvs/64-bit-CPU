class SpecFetchFence:
    """Model of a speculative fetch fence that blocks subsequent loads
    until preceding branches are retired."""
    def __init__(self):
        self.pending = 0

    def fence(self):
        """Insert a fence after a branch prediction."""
        self.pending += 1

    def retire_branch(self):
        """Call when a predicted branch retires."""
        if self.pending > 0:
            self.pending -= 1

    def allow_load(self) -> bool:
        """Return True when loads may proceed."""
        return self.pending == 0
