class BranchUnit:
    """Python model of the branch_unit."""

    BEQ  = 0
    BNE  = 1
    BLT  = 2
    BGE  = 3
    BLTU = 4
    BGEU = 5
    JAL  = 6
    JALR = 7

    def __init__(self):
        pass

    @staticmethod
    def _to_signed(val):
        return val if val < (1 << 63) else val - (1 << 64)

    def compute(self, branch_ctrl, rs1_val, rs2_val, pc, imm,
                predicted_taken=False, predicted_target=0):
        """Resolve a branch and report misprediction."""
        imm = imm & 0xFFFFFFFF
        if imm & (1 << 31):
            imm -= 1 << 32
        target = (pc + imm) & 0xFFFFFFFFFFFFFFFF
        taken = False
        if branch_ctrl == self.BEQ:
            taken = rs1_val == rs2_val
        elif branch_ctrl == self.BNE:
            taken = rs1_val != rs2_val
        elif branch_ctrl == self.BLT:
            taken = self._to_signed(rs1_val) < self._to_signed(rs2_val)
        elif branch_ctrl == self.BGE:
            taken = self._to_signed(rs1_val) >= self._to_signed(rs2_val)
        elif branch_ctrl == self.BLTU:
            taken = rs1_val < rs2_val
        elif branch_ctrl == self.BGEU:
            taken = rs1_val >= rs2_val
        elif branch_ctrl == self.JAL:
            taken = True
        elif branch_ctrl == self.JALR:
            taken = True
            target = (rs1_val + imm) & 0xFFFFFFFFFFFFFFFE
        actual_target = target if taken else (pc + 4) & 0xFFFFFFFFFFFFFFFF
        mispredict = (predicted_taken != taken or
                      (predicted_taken and taken and predicted_target != actual_target))
        return {
            "taken": taken,
            "target": actual_target,
            "mispredict": mispredict,
        }
