class IntALU2:
    """Python model of the int_alu2 dual ALU unit."""

    ALU_ADD = 0
    ALU_SUB = 1
    ALU_AND = 2
    ALU_OR  = 3
    ALU_XOR = 4
    ALU_SLL = 5
    ALU_SRL = 6
    ALU_SRA = 7

    def __init__(self):
        pass

    def cycle(self, ops):
        """Execute up to two operations in a single cycle.

        *ops* is a list of up to two dictionaries with fields:
            - ``op1``: first operand
            - ``op2``: second operand
            - ``alu_ctrl``: operation selector
            - ``dest``: destination register index
            - ``rob``: reorder buffer index
        Returns a list of result dictionaries (or ``None``).
        """
        results = [None, None]
        for idx, op in enumerate(ops):
            if op is None:
                continue
            op1 = op.get("op1", 0) & 0xFFFFFFFFFFFFFFFF
            op2 = op.get("op2", 0) & 0xFFFFFFFFFFFFFFFF
            ctrl = op.get("alu_ctrl", self.ALU_ADD)
            if ctrl == self.ALU_ADD:
                data = (op1 + op2) & 0xFFFFFFFFFFFFFFFF
            elif ctrl == self.ALU_SUB:
                data = (op1 - op2) & 0xFFFFFFFFFFFFFFFF
            elif ctrl == self.ALU_AND:
                data = op1 & op2
            elif ctrl == self.ALU_OR:
                data = op1 | op2
            elif ctrl == self.ALU_XOR:
                data = op1 ^ op2
            elif ctrl == self.ALU_SLL:
                data = (op1 << (op2 & 0x3F)) & 0xFFFFFFFFFFFFFFFF
            elif ctrl == self.ALU_SRL:
                data = (op1 >> (op2 & 0x3F)) & 0xFFFFFFFFFFFFFFFF
            elif ctrl == self.ALU_SRA:
                shamt = op2 & 0x3F
                if op1 & (1 << 63):
                    data = ((op1 >> shamt) | (0xFFFFFFFFFFFFFFFF << (64 - shamt))) & 0xFFFFFFFFFFFFFFFF
                else:
                    data = (op1 >> shamt) & 0xFFFFFFFFFFFFFFFF
            else:
                data = 0
            results[idx] = {
                "result": data,
                "dest": op.get("dest"),
                "rob": op.get("rob"),
            }
        return results
