from rtl.decode.decoder8w import Decoder8W


class GoldenModel:
    """Minimal RISC-V golden reference supporting a small subset of RV64I."""

    def __init__(self, pc=0, *, coverage=None):
        self.regs = [0] * 32
        self.fregs = [0] * 32  # store double precision bits
        self.vregs = [0] * 32  # 512-bit vector registers
        self.mem = {}
        self.csrs = {0xC00: 0, 0xC02: 0}  # cycle and instret counters
        self.pc = pc
        self._reservation = None
        self.last_exception = None
        self.MASK64 = 0xFFFFFFFFFFFFFFFF
        self.MASK512 = (1 << 512) - 1
        self.coverage = coverage
        self.page_table = {}

    def load_memory(self, addr, data, *, map_va=None, perm="rw"):
        """Load 64-bit word at *addr*.

        ``map_va`` optionally creates a virtual to physical translation
        for the given address using ``perm`` permissions. If no mapping
        exists, an identity mapping is created so existing tests that
        use physical addresses directly continue to work.
        """
        self.mem[addr] = data & 0xFFFFFFFFFFFFFFFF
        va = map_va if map_va is not None else addr
        if va not in self.page_table:
            self.page_table[va] = (addr, perm)

    def fetch(self, addr):
        return self.mem.get(addr, 0)

    def get_last_exception(self):
        """Return the last exception string or ``None``."""
        return self.last_exception

    @staticmethod
    def _sign_extend(value, bits):
        mask = 1 << (bits - 1)
        return (value & (mask - 1)) - (value & mask)

    @staticmethod
    def _to_signed(val):
        return val if val < 2**63 else val - 2**64

    @staticmethod
    def _bits_to_double(val):
        import struct
        return struct.unpack('<d', val.to_bytes(8, 'little'))[0]

    @staticmethod
    def _double_to_bits(fval):
        import struct
        return int.from_bytes(struct.pack('<d', fval), 'little') & 0xFFFFFFFFFFFFFFFF

    def map_page(self, va, pa, perm="rw"):
        """Map *va* to *pa* with the given permissions."""
        self.page_table[va] = (pa, perm)

    def translate(self, va, perm):
        """Translate a virtual address returning ``(pa, fault)``.

        Records page walk coverage if available.
        """
        if va not in self.page_table:
            # allow direct physical addressing for legacy tests
            pa = va
            fault = va not in self.mem
        else:
            pa, permissions = self.page_table[va]
            fault = perm not in permissions
        if self.coverage:
            self.coverage.record_page_walk(fault)
        return pa, fault

    def step(self, instr):
        self.last_exception = None
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F

        # update cycle and instret counters
        self.csrs[0xC00] = (self.csrs.get(0xC00, 0) + 1) & 0xFFFFFFFFFFFFFFFF
        self.csrs[0xC02] = (self.csrs.get(0xC02, 0) + 1) & 0xFFFFFFFFFFFFFFFF

        next_pc = self.pc + 4
        taken = False

        if opcode == 0x33:  # R-type
            if funct7 == 0x00 and funct3 == 0x0:  # ADD
                self.regs[rd] = (self.regs[rs1] + self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x20 and funct3 == 0x0:  # SUB
                self.regs[rd] = (self.regs[rs1] - self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x00 and funct3 == 0x2:  # SLT
                self.regs[rd] = 1 if self._to_signed(self.regs[rs1]) < self._to_signed(self.regs[rs2]) else 0
            elif funct7 == 0x00 and funct3 == 0x3:  # SLTU
                self.regs[rd] = 1 if self.regs[rs1] < self.regs[rs2] else 0
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

            imm = self._sign_extend(instr >> 20, 12)
            if funct3 == 0x0:  # ADDI
                self.regs[rd] = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x7:  # ANDI
                self.regs[rd] = self.regs[rs1] & (imm & 0xFFFFFFFFFFFFFFFF)
            elif funct3 == 0x6:  # ORI
                self.regs[rd] = (self.regs[rs1] | imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x4:  # XORI
                self.regs[rd] = (self.regs[rs1] ^ imm) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x2:  # SLTI
                self.regs[rd] = 1 if self._to_signed(self.regs[rs1]) < imm else 0
            elif funct3 == 0x3:  # SLTIU
                self.regs[rd] = 1 if self.regs[rs1] < (imm & 0xFFFFFFFFFFFFFFFF) else 0
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
                self.last_exception = "illegal"
        elif opcode == 0x03:  # Loads
            imm = self._sign_extend(instr >> 20, 12)
            va = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            pa, fault = self.translate(va, 'r')
            misalign = False
            case_align = {
                0x1: 2,
                0x2: 4,
                0x3: 8,
                0x5: 2,
                0x6: 4,
            }
            align = case_align.get(funct3, 1)
            if va % align != 0:
                misalign = align > 1
            if misalign:
                self.last_exception = "misalign"

            elif fault or pa not in self.mem:
                self.last_exception = "page"

            elif funct3 == 0x0:  # LB
                data = self.mem.get(pa, 0) & 0xFF
                self.regs[rd] = self._sign_extend(data, 8) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x1:  # LH
                data = self.mem.get(pa, 0) & 0xFFFF
                self.regs[rd] = self._sign_extend(data, 16) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x2:  # LW
                data = self.mem.get(pa, 0) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(data, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x3:  # LD
                self.regs[rd] = self.mem.get(pa, 0) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x4:  # LBU
                self.regs[rd] = self.mem.get(pa, 0) & 0xFF
            elif funct3 == 0x5:  # LHU
                self.regs[rd] = self.mem.get(pa, 0) & 0xFFFF
            elif funct3 == 0x6:  # LWU
                self.regs[rd] = self.mem.get(pa, 0) & 0xFFFFFFFF
            else:
                self.last_exception = "illegal"
        elif opcode == 0x23:  # Stores
            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            imm = self._sign_extend(imm, 12)
            va = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            pa, fault = self.translate(va, 'w')
            misalign = False
            case_align = {
                0x1: 2,
                0x2: 4,
                0x3: 8,
            }
            align = case_align.get(funct3, 1)
            if va % align != 0:
                misalign = align > 1
            if misalign:
                self.last_exception = "misalign"
            elif fault:
                self.last_exception = "page"
            elif funct3 == 0x0:  # SB
                self.mem[pa] = self.regs[rs2] & 0xFF
            elif funct3 == 0x1:  # SH
                self.mem[pa] = self.regs[rs2] & 0xFFFF
            elif funct3 == 0x2:  # SW
                self.mem[pa] = self.regs[rs2] & 0xFFFFFFFF
            elif funct3 == 0x3:  # SD
                self.mem[pa] = self.regs[rs2] & 0xFFFFFFFFFFFFFFFF
            else:
                self.last_exception = "illegal"
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
        elif opcode == 0x73:  # SYSTEM / CSR ops
            csr = (instr >> 20) & 0xFFF
            uimm = (instr >> 15) & 0x1F
            csr_val = self.csrs.get(csr, 0)
            if funct3 == 0x1:  # CSRRW
                self.csrs[csr] = self.regs[rs1]
                self.regs[rd] = csr_val
            elif funct3 == 0x2:  # CSRRS
                self.csrs[csr] = csr_val | self.regs[rs1]
                self.regs[rd] = csr_val
            elif funct3 == 0x3:  # CSRRC
                self.csrs[csr] = csr_val & (~self.regs[rs1] & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = csr_val
            elif funct3 == 0x5:  # CSRRWI
                self.csrs[csr] = uimm
                self.regs[rd] = csr_val
            elif funct3 == 0x6:  # CSRRSI
                self.csrs[csr] = csr_val | uimm
                self.regs[rd] = csr_val
            elif funct3 == 0x7:  # CSRRCI
                self.csrs[csr] = csr_val & (~uimm & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = csr_val
            else:
                self.last_exception = "illegal"
        elif opcode == 0x53:  # Floating point
            if funct7 == 0x01 and funct3 == 0x0:  # FADD.D
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                res = a + b
                self.fregs[rd] = self._double_to_bits(res)
            else:
                self.last_exception = "illegal"
        elif opcode == 0x07:  # Vector load (VLE64.V)
            imm = self._sign_extend(instr >> 20, 12)
            addr = (self.regs[rs1] + imm) & self.MASK64
            misalign = addr % 8 != 0
            if misalign:
                self.last_exception = "misalign"
            else:
                vec = 0
                for i in range(8):
                    if addr + i * 8 not in self.mem:
                        self.last_exception = "page"
                        break
                    vec |= (self.mem.get(addr + i * 8, 0) & self.MASK64) << (64 * i)
                if self.last_exception is None:
                    self.vregs[rd] = vec & self.MASK512
        elif opcode == 0x27:  # Vector store (VSE64.V)
            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            imm = self._sign_extend(imm, 12)
            addr = (self.regs[rs1] + imm) & self.MASK64
            misalign = addr % 8 != 0
            if misalign:
                self.last_exception = "misalign"
            else:
                for i in range(8):
                    self.mem[addr + i * 8] = (self.vregs[rs2] >> (64 * i)) & self.MASK64
        elif opcode == 0x57:  # Vector arithmetic
            funct6 = (instr >> 26) & 0x3F
            if funct6 == 0x00 and funct3 == 0x0:  # VADD.VV
                res = 0
                for i in range(8):
                    a = (self.vregs[rs1] >> (64 * i)) & self.MASK64
                    b = (self.vregs[rs2] >> (64 * i)) & self.MASK64
                    res |= ((a + b) & self.MASK64) << (64 * i)
                self.vregs[rd] = res
            else:
                self.last_exception = "illegal"
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
        else:
            self.last_exception = "illegal"
        self.pc = next_pc
        return next_pc

    def execute_bundle(self, instructions):
        for instr in instructions:
            self.step(instr)
        return self.pc

    def issue_bundle(self, pc, instructions, *, coverage=None):
        """Decode and execute up to eight instructions starting at *pc*.

        Returns a tuple ``(uops, next_pc)`` where ``uops`` is the list of
        decoded micro-operations produced by :class:`Decoder8W` and ``next_pc``
        is the PC after executing the bundle.
        """
        self.pc = pc
        decoder = Decoder8W()
        uops = decoder.decode(instructions, coverage=coverage)
        next_pc = self.execute_bundle(instructions)
        return uops, next_pc
