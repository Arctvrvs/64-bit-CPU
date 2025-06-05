class PCFetch:
    """Simple PC generator model."""

    def __init__(self, reset_vector=0x80000000):
        self.reset_vector = reset_vector
        self.pc = reset_vector

    def reset(self):
        self.pc = self.reset_vector

    def step(self, branch_taken=False, branch_target=0):
        if branch_taken:
            self.pc = branch_target & 0xFFFFFFFFFFFFFFFF
        else:
            self.pc = (self.pc + 8) & 0xFFFFFFFFFFFFFFFF
        return self.pc

    def pc_if2(self):
        return self.pc

    def pc_if1_plus8(self):
        return (self.pc + 8) & 0xFFFFFFFFFFFFFFFF
