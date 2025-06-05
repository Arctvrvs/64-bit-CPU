class AmoUnit:
    """Python model of the amo_unit executing basic atomic operations."""

    AMO_ADD = 0
    AMO_SWAP = 1

    def compute(self, op_a, op_b, amo_funct):
        """Return the result of the specified atomic operation."""
        if amo_funct == self.AMO_ADD:
            return (op_a + op_b) & 0xFFFFFFFFFFFFFFFF
        elif amo_funct == self.AMO_SWAP:
            return op_b & 0xFFFFFFFFFFFFFFFF
        else:
            return op_a & 0xFFFFFFFFFFFFFFFF
