class GoldenModel:
    """Minimal RISC-V golden reference supporting a small subset of RV64I."""

    def __init__(self, pc=0):
        self.regs = [0] * 32
        self.mem = {}
        self.pc = pc

    def load_memory(self, addr, data):
        """Load 64-bit word at addr."""
        self.mem[addr] = data & 0xFFFFFFFFFFFFFFFF

    def fetch(self, addr):
        return self.mem.get(addr, 0)

    @staticmethod
    def _sign_extend(value, bits):
        mask = 1 << (bits - 1)
        return (value & (mask - 1)) - (value & mask)

    def step(self, instr):
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F

        next_pc = self.pc + 4
        taken = False

        if opcode == 0x33:  # R-type
            if funct3 == 0x0 and funct7 == 0x00:  # ADD
                self.regs[rd] = (self.regs[rs1] + self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x0 and funct7 == 0x20:  # SUB
                self.regs[rd] = (self.regs[rs1] - self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x13:  # ADDI
            imm = self._sign_extend(instr >> 20, 12)
            self.regs[rd] = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x03:  # LW (simplified to 64-bit)
            imm = self._sign_extend(instr >> 20, 12)
            addr = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            self.regs[rd] = self.mem.get(addr, 0)
        elif opcode == 0x23:  # SW (simplified to 64-bit)
            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            imm = self._sign_extend(imm, 12)
            addr = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            self.mem[addr] = self.regs[rs2] & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x63:  # Branches
            imm = ((instr >> 7) & 0x1E) | ((instr >> 20) & 0x7E0)
            imm |= ((instr >> 7) & 0x1) << 11
            imm |= (instr >> 31) << 12
            imm = self._sign_extend(imm, 13)
            if funct3 == 0x0:  # BEQ
                taken = self.regs[rs1] == self.regs[rs2]
            elif funct3 == 0x1:  # BNE
                taken = self.regs[rs1] != self.regs[rs2]
            if taken:
                next_pc = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF
        self.pc = next_pc
        return next_pc

    def execute_bundle(self, instructions):
        for instr in instructions:
            self.step(instr)
        return self.pc
