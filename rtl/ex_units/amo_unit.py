class AmoUnit:
    """Python model of the amo_unit executing basic atomic operations."""

    AMO_ADD = 0x00
    AMO_SWAP = 0x01
    AMO_XOR = 0x04
    AMO_OR = 0x08
    AMO_AND = 0x0C
    AMO_MIN = 0x10
    AMO_MAX = 0x14
    AMO_MINU = 0x18
    AMO_MAXU = 0x1C

    def compute(self, op_a, op_b, amo_funct):
        """Return the result of the specified atomic operation."""
        if amo_funct == self.AMO_ADD:
            return (op_a + op_b) & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_SWAP:
            return op_b & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_XOR:
            return (op_a ^ op_b) & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_OR:
            return (op_a | op_b) & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_AND:
            return (op_a & op_b) & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_MIN:
            a = op_a if op_a < 2**63 else op_a - 2**64
            b = op_b if op_b < 2**63 else op_b - 2**64
            return a if a < b else b & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_MAX:
            a = op_a if op_a < 2**63 else op_a - 2**64
            b = op_b if op_b < 2**63 else op_b - 2**64
            return a if a > b else b & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_MINU:
            return op_a if op_a < op_b else op_b & 0xFFFFFFFFFFFFFFFF
        if amo_funct == self.AMO_MAXU:
            return op_a if op_a > op_b else op_b & 0xFFFFFFFFFFFFFFFF
        return op_a & 0xFFFFFFFFFFFFFFFF
