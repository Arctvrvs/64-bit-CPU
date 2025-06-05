class GoldenModel:
    """Minimal RISC-V golden reference supporting a small subset of RV64I."""

    def __init__(self, pc=0):
        self.regs = [0] * 32
        self.mem = {}
        self.pc = pc
        self._reservation = None

    def load_memory(self, addr, data):
        """Load 64-bit word at addr."""
        self.mem[addr] = data & 0xFFFFFFFFFFFFFFFF

    def fetch(self, addr):
        return self.mem.get(addr, 0)

    @staticmethod
    def _sign_extend(value, bits):
        mask = 1 << (bits - 1)
        return (value & (mask - 1)) - (value & mask)

    @staticmethod
    def _to_signed(val):
        return val if val < 2**63 else val - 2**64

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
            if funct7 == 0x00 and funct3 == 0x0:  # ADD
                self.regs[rd] = (self.regs[rs1] + self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x20 and funct3 == 0x0:  # SUB
                self.regs[rd] = (self.regs[rs1] - self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF

            elif funct7 == 0x00 and funct3 == 0x7:  # AND
                self.regs[rd] = self.regs[rs1] & self.regs[rs2]
            elif funct7 == 0x00 and funct3 == 0x6:  # OR
                self.regs[rd] = self.regs[rs1] | self.regs[rs2]
            elif funct7 == 0x00 and funct3 == 0x4:  # XOR
                self.regs[rd] = self.regs[rs1] ^ self.regs[rs2]
            elif funct7 == 0x00 and funct3 == 0x1:  # SLL
                shamt = self.regs[rs2] & 0x3F
                self.regs[rd] = (self.regs[rs1] << shamt) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x00 and funct3 == 0x5:  # SRL
                shamt = self.regs[rs2] & 0x3F
                self.regs[rd] = (self.regs[rs1] >> shamt) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x20 and funct3 == 0x5:  # SRA
                shamt = self.regs[rs2] & 0x3F
                self.regs[rd] = (self._to_signed(self.regs[rs1]) >> shamt) & 0xFFFFFFFFFFFFFFFF

            elif funct7 == 0x01:  # RV64M extension
                if funct3 == 0x0:  # MUL
                    self.regs[rd] = (self.regs[rs1] * self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
                elif funct3 == 0x1:  # MULH
                    a = self.regs[rs1]
                    b = self.regs[rs2]
                    a_s = a if a < 2**63 else a - 2**64
                    b_s = b if b < 2**63 else b - 2**64
                    res = (a_s * b_s) >> 64
                    self.regs[rd] = res & 0xFFFFFFFFFFFFFFFF
                elif funct3 == 0x2:  # MULHSU
                    a = self.regs[rs1]
                    b = self.regs[rs2]
                    a_s = a if a < 2**63 else a - 2**64
                    res = (a_s * b) >> 64
                    self.regs[rd] = res & 0xFFFFFFFFFFFFFFFF
                elif funct3 == 0x3:  # MULHU
                    a = self.regs[rs1]
                    b = self.regs[rs2]
                    res = (a * b) >> 64
                    self.regs[rd] = res & 0xFFFFFFFFFFFFFFFF
                elif funct3 == 0x4:  # DIV
                    dividend = self.regs[rs1]
                    divisor = self.regs[rs2]
                    if divisor == 0:
                        self.regs[rd] = 0xFFFFFFFFFFFFFFFF
                    else:
                        dividend_s = dividend if dividend < 2**63 else dividend - 2**64
                        divisor_s = divisor if divisor < 2**63 else divisor - 2**64
                        self.regs[rd] = (int(dividend_s / divisor_s) & 0xFFFFFFFFFFFFFFFF)
                elif funct3 == 0x5:  # DIVU
                    dividend = self.regs[rs1]
                    divisor = self.regs[rs2]
                    if divisor == 0:
                        self.regs[rd] = 0xFFFFFFFFFFFFFFFF
                    else:
                        self.regs[rd] = (dividend // divisor) & 0xFFFFFFFFFFFFFFFF
                elif funct3 == 0x6:  # REM
                    dividend = self.regs[rs1]
                    divisor = self.regs[rs2]
                    if divisor == 0:
                        self.regs[rd] = dividend & 0xFFFFFFFFFFFFFFFF
                    else:
                        dividend_s = dividend if dividend < 2**63 else dividend - 2**64
                        divisor_s = divisor if divisor < 2**63 else divisor - 2**64
                        self.regs[rd] = (int(dividend_s % divisor_s) & 0xFFFFFFFFFFFFFFFF)
                elif funct3 == 0x7:  # REMU
                    dividend = self.regs[rs1]
                    divisor = self.regs[rs2]
                    if divisor == 0:
                        self.regs[rd] = dividend & 0xFFFFFFFFFFFFFFFF
                    else:
                        self.regs[rd] = (dividend % divisor) & 0xFFFFFFFFFFFFFFFF
               elif opcode == 0x13:  # I-type arith
               elif opcode == 0x13:  # ADDI
            imm = self._sign_extend(instr >> 20, 12)
            if funct3 == 0x0:  # ADDI
                self.regs[rd] = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x7:  # ANDI
                self.regs[rd] = self.regs[rs1] & (imm & 0xFFFFFFFFFFFFFFFF)
            elif funct3 == 0x6:  # ORI
                self.regs[rd] = (self.regs[rs1] | imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x4:  # XORI
                self.regs[rd] = (self.regs[rs1] ^ imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x1 and funct7 == 0x00:  # SLLI
                shamt = (instr >> 20) & 0x3F
                self.regs[rd] = (self.regs[rs1] << shamt) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x5 and funct7 == 0x00:  # SRLI
                shamt = (instr >> 20) & 0x3F
                self.regs[rd] = (self.regs[rs1] >> shamt) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x5 and funct7 == 0x20:  # SRAI
                shamt = (instr >> 20) & 0x3F
                self.regs[rd] = (self._to_signed(self.regs[rs1]) >> shamt) & 0xFFFFFFFFFFFFFFFF
            else:
                pass
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
            elif funct3 == 0x4:  # BLT
                taken = self._to_signed(self.regs[rs1]) < self._to_signed(self.regs[rs2])
            elif funct3 == 0x5:  # BGE
                taken = self._to_signed(self.regs[rs1]) >= self._to_signed(self.regs[rs2])
            elif funct3 == 0x6:  # BLTU
                taken = self.regs[rs1] < self.regs[rs2]
            elif funct3 == 0x7:  # BGEU
                taken = self.regs[rs1] >= self.regs[rs2]
            if taken:
                next_pc = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x6F:  # JAL
            imm = ((instr >> 21) & 0x3FF) | ((instr >> 20) & 0x1) << 10
            imm |= ((instr >> 12) & 0xFF) << 11
            imm |= (instr >> 31) << 19
            imm = self._sign_extend(imm << 1, 21)
            self.regs[rd] = (self.pc + 4) & 0xFFFFFFFFFFFFFFFF
            next_pc = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x67:  # JALR
            imm = self._sign_extend(instr >> 20, 12)
            self.regs[rd] = (self.pc + 4) & 0xFFFFFFFFFFFFFFFF
            next_pc = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFE
        elif opcode == 0x37:  # LUI
            imm = instr & 0xFFFFF000
            self.regs[rd] = imm
        elif opcode == 0x17:  # AUIPC
            imm = instr & 0xFFFFF000
            self.regs[rd] = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF

        elif opcode == 0x2F:  # Atomic memory ops
            funct5 = (instr >> 27) & 0x1F
            aq    = (instr >> 26) & 1
            rl    = (instr >> 25) & 1
            addr = self.regs[rs1]
            if funct5 == 0x02:  # LR.D
                self.regs[rd] = self.mem.get(addr, 0)
                self._reservation = addr
            elif funct5 == 0x03:  # SC.D
                if self._reservation == addr:
                    self.mem[addr] = self.regs[rs2] & 0xFFFFFFFFFFFFFFFF
                    self.regs[rd] = 0
                else:
                    self.regs[rd] = 1
                self._reservation = None
            elif funct5 == 0x00:  # AMOADD.D
                tmp = self.mem.get(addr, 0)
                self.mem[addr] = (tmp + self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
                self.regs[rd] = tmp
            elif funct5 == 0x01:  # AMOSWAP.D
                tmp = self.mem.get(addr, 0)
                self.mem[addr] = self.regs[rs2] & 0xFFFFFFFFFFFFFFFF
                self.regs[rd] = tmp
        self.pc = next_pc
        return next_pc

    def execute_bundle(self, instructions):
        for instr in instructions:
            self.step(instr)
        return self.pc
