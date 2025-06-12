from rtl.decode.decoder8w import Decoder8W
from rtl.vm import VMCS, EPT
from rtl.security.sgx_enclave import SGXEnclave
from rtl.security.sev_memory import SEVMemory
from rtl.security.spec_fetch_fence import SpecFetchFence
from rtl.mmu import TlbL1, TlbL2, PageWalker8


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
        self.tlb_l1 = TlbL1(coverage=coverage)
        self.tlb_l2 = TlbL2(coverage=coverage)
        self.walker = PageWalker8(coverage=coverage)
        self.vmcs = VMCS()
        self.ept = EPT()
        self.sgx = SGXEnclave()
        self.sev = SEVMemory()
        self.spec_fence = SpecFetchFence()
        self.priv_level = 0  # 0=kernel, 1=user
        self.smep = 0
        self.smap = 0
        self.smap_override = 0
        self.meltdown_protect = True

    def load_memory(self, addr, data, *, map_va=None, perm="rw"):
        """Load 64-bit word at *addr*.

        ``map_va`` optionally creates a virtual to physical translation
        for the given address using ``perm`` permissions. If no mapping
        exists, an identity mapping is created so existing tests that
        use physical addresses directly continue to work.
        """
        self._mem_store(addr, data & 0xFFFFFFFFFFFFFFFF)
        va = map_va if map_va is not None else addr
        if va not in self.page_table:
            self.map_page(va, addr, perm=perm)

    def fetch(self, addr):
        return self._mem_load(addr)

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
        self.walker.set_entry(va, pa, perm=perm)

    # ------------------------------------------------------------------
    # SEV memory helpers
    # ------------------------------------------------------------------
    def set_sev_key(self, key: int):
        """Set the memory encryption key."""
        self.sev.set_key(key)

    def set_meltdown_protect(self, enable: bool):
        """Enable or disable Meltdown-style protection."""
        self.meltdown_protect = bool(enable)

    def _sev_addr(self, pa: int) -> int:
        """Return the encrypted physical address used for memory access."""
        return pa ^ self.sev.key

    def _mem_load(self, pa: int) -> int:
        enc = self.mem.get(self._sev_addr(pa), 0)
        return self.sev.decrypt(enc)

    def _mem_store(self, pa: int, value: int):
        self.mem[self._sev_addr(pa)] = self.sev.encrypt(value & self.MASK64)

    def reset(self, pc=0):
        """Reset architectural state and optionally set a new PC."""
        self.__init__(pc=pc, coverage=self.coverage)

    def translate(self, va, perm, *, is_exec=False, override=False):
        """Translate a virtual address returning ``(pa, fault)``.

        ``perm`` is ``'r'`` for read, ``'w'`` for write or ``'x'`` for
        instruction fetch. ``is_exec`` should be set when translating an
        instruction fetch so SMEP/NX checks apply. ``override`` is used to
        bypass SMAP for certain string operations.

        The method returns ``(pa, fault_code)`` where ``fault_code`` is a
        string like ``"page"``, ``"nx"``, ``"smep"`` or ``"smap"`` or ``None``
        if the translation succeeds.
        """
        if va not in self.page_table:
            self.map_page(va, va, perm="rwx")

        hit, pa, flt = self.tlb_l1.lookup(va, perm=perm)
        fault = "page" if flt else None
        if not hit:
            hit, pa, flt = self.tlb_l2.lookup(va, perm=perm)
            if flt:
                fault = "page"
            if hit:
                if (va & 0xFFF) == (pa & 0xFFF):
                    self.tlb_l1.refill(va, pa, perm="rwx")
        if not hit:
            pa, walk_fault = self.walker.walk(va, perm=perm)
            if walk_fault:
                fault = "page"
            else:
                if (va & 0xFFF) == (pa & 0xFFF):
                    self.tlb_l2.refill(va, pa, perm="rwx")
                    self.tlb_l1.refill(va, pa, perm="rwx")

        if va in self.page_table:
            _, permissions = self.page_table[va]
            user = "u" in permissions
            if fault is None and perm not in permissions:
                fault = "page"
        else:
            permissions = "rwx"
            user = False

        if is_exec and "x" not in permissions:
            fault = "nx"
        if self.priv_level == 0 and user:
            if is_exec and self.smep:
                fault = "smep"
            elif not is_exec and self.smap and not override:
                fault = "smap"

        if self.coverage:
            self.coverage.record_page_walk(fault is not None)
        if self.vmcs.running:
            pa = self.ept.translate(self.vmcs.current_vmid(), pa)
        if fault is None and self.sgx.access(pa):
            fault = "sgx"
        return pa, fault

    def step(self, instr):
        self.last_exception = None
        if self.pc in self.page_table:
            pa, fault = self.translate(self.pc, 'x', is_exec=True)
            if fault:
                self.last_exception = fault
                self.pc = (self.pc + 4) & self.MASK64
                return
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
        elif opcode == 0x3B:  # R-type 32-bit
            if funct7 == 0x00 and funct3 == 0x0:  # ADDW
                res = (self.regs[rs1] + self.regs[rs2]) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x20 and funct3 == 0x0:  # SUBW
                res = (self.regs[rs1] - self.regs[rs2]) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x00 and funct3 == 0x1:  # SLLW
                shamt = self.regs[rs2] & 0x1F
                res = (self.regs[rs1] << shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x00 and funct3 == 0x5:  # SRLW
                shamt = self.regs[rs2] & 0x1F
                res = (self.regs[rs1] >> shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct7 == 0x20 and funct3 == 0x5:  # SRAW
                shamt = self.regs[rs2] & 0x1F
                val = self._sign_extend(self.regs[rs1] & 0xFFFFFFFF, 32)
                res = (val >> shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
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
        elif opcode == 0x1B:  # I-type arith 32-bit
            imm = self._sign_extend(instr >> 20, 12)
            if funct3 == 0x0:  # ADDIW
                res = (self.regs[rs1] + imm) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x1 and funct7 == 0x00:  # SLLIW
                shamt = (instr >> 20) & 0x1F
                res = (self.regs[rs1] << shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x5 and funct7 == 0x00:  # SRLIW
                shamt = (instr >> 20) & 0x1F
                res = (self.regs[rs1] >> shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            elif funct3 == 0x5 and funct7 == 0x20:  # SRAIW
                shamt = (instr >> 20) & 0x1F
                val = self._sign_extend(self.regs[rs1] & 0xFFFFFFFF, 32)
                res = (val >> shamt) & 0xFFFFFFFF
                self.regs[rd] = self._sign_extend(res, 32) & 0xFFFFFFFFFFFFFFFF
            else:
                self.last_exception = "illegal"
        elif opcode == 0x03:  # Loads
            if not self.spec_fence.allow_load():
                self.last_exception = "spec"
            else:
                imm = self._sign_extend(instr >> 20, 12)
                va = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
                pa, fault = self.translate(
                    va, 'r', is_exec=False, override=self.smap_override
                )
                align_tbl = {0x1: 2, 0x2: 4, 0x3: 8, 0x5: 2, 0x6: 4}
                align = align_tbl.get(funct3, 1)
                data = self._mem_load(pa) if (not self.meltdown_protect and self._sev_addr(pa) in self.mem) else None
                if va % align != 0:
                    self.last_exception = "misalign" if align > 1 else None
                elif fault:
                    self.last_exception = fault
                elif self._sev_addr(pa) not in self.mem:
                    self.last_exception = "page"
                if self.last_exception is None or not self.meltdown_protect:
                    if data is None:
                        data = self._mem_load(pa)
                    if funct3 == 0x0:  # LB
                        val = self._sign_extend(data & 0xFF, 8)
                    elif funct3 == 0x1:  # LH
                        val = self._sign_extend(data & 0xFFFF, 16)
                    elif funct3 == 0x2:  # LW
                        val = self._sign_extend(data & 0xFFFFFFFF, 32)
                    elif funct3 == 0x3:  # LD
                        val = data & 0xFFFFFFFFFFFFFFFF
                    elif funct3 == 0x4:  # LBU
                        val = data & 0xFF
                    elif funct3 == 0x5:  # LHU
                        val = data & 0xFFFF
                    elif funct3 == 0x6:  # LWU
                        val = data & 0xFFFFFFFF
                    else:
                        self.last_exception = "illegal"
                        val = None
                    if val is not None:
                        self.regs[rd] = val & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x23:  # Stores
            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            imm = self._sign_extend(imm, 12)
            va = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFF
            pa, fault = self.translate(va, 'w', is_exec=False, override=self.smap_override)
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
                self.last_exception = fault
            elif self._sev_addr(pa) not in self.mem:
                self.last_exception = "page"
            elif funct3 == 0x0:  # SB
                self._mem_store(pa, self.regs[rs2] & 0xFF)
            elif funct3 == 0x1:  # SH
                self._mem_store(pa, self.regs[rs2] & 0xFFFF)
            elif funct3 == 0x2:  # SW
                self._mem_store(pa, self.regs[rs2] & 0xFFFFFFFF)
            elif funct3 == 0x3:  # SD
                self._mem_store(pa, self.regs[rs2] & 0xFFFFFFFFFFFFFFFF)
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
            self.spec_fence.retire_branch()
        elif opcode == 0x6F:  # JAL
            imm = ((instr >> 21) & 0x3FF) | ((instr >> 20) & 0x1) << 10
            imm |= ((instr >> 12) & 0xFF) << 11
            imm |= (instr >> 31) << 19
            imm = self._sign_extend(imm << 1, 21)
            self.regs[rd] = (self.pc + 4) & 0xFFFFFFFFFFFFFFFF
            next_pc = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF
            self.spec_fence.retire_branch()
        elif opcode == 0x67:  # JALR
            imm = self._sign_extend(instr >> 20, 12)
            self.regs[rd] = (self.pc + 4) & 0xFFFFFFFFFFFFFFFF
            next_pc = (self.regs[rs1] + imm) & 0xFFFFFFFFFFFFFFFE
            self.spec_fence.retire_branch()
        elif opcode == 0x37:  # LUI
            imm = instr & 0xFFFFF000
            self.regs[rd] = imm
        elif opcode == 0x17:  # AUIPC
            imm = instr & 0xFFFFF000
            self.regs[rd] = (self.pc + imm) & 0xFFFFFFFFFFFFFFFF
        elif opcode == 0x0F:  # FENCE/FENCE.I/SpecFence
            if funct3 == 0x0:  # FENCE
                pass  # no operation in the model
            elif funct3 == 0x1:  # FENCE.I
                pass
            elif funct3 == 0x2:  # SpecFetchFence
                self.spec_fence.fence()
            else:
                self.last_exception = "illegal"
        elif opcode == 0x73:  # SYSTEM / CSR ops
            csr = (instr >> 20) & 0xFFF
            uimm = (instr >> 15) & 0x1F
            csr_val = self.csrs.get(csr, 0)
            if funct3 == 0x0:  # ECALL/EBREAK
                if instr >> 20 == 0:
                    self.last_exception = "ecall"
                elif instr >> 20 == 1:
                    self.last_exception = "ebreak"
                else:
                    self.last_exception = "illegal"
            elif funct3 == 0x1:  # CSRRW
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
            elif funct7 == 0x05 and funct3 == 0x0:  # FSUB.D
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                res = a - b
                self.fregs[rd] = self._double_to_bits(res)
            elif funct7 == 0x09 and funct3 == 0x0:  # FMUL.D
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                res = a * b
                self.fregs[rd] = self._double_to_bits(res)
            elif funct7 == 0x0D and funct3 == 0x0:  # FDIV.D
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                try:
                    res = a / b
                except ZeroDivisionError:
                    res = float('inf') if a >= 0 else float('-inf')
                self.fregs[rd] = self._double_to_bits(res)
            elif funct7 == 0x15:  # FMIN.D/FMAX.D
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                if ((instr >> 12) & 7) & 1:
                    res = max(a, b)
                else:
                    res = min(a, b)
                self.fregs[rd] = self._double_to_bits(res)
            else:
                self.last_exception = "illegal"
        elif opcode in (0x43, 0x47, 0x4B, 0x4F):  # FMADD.D/FMSUB.D/FNMSUB.D/FNMADD.D
            fmt = (instr >> 25) & 0x3
            rs3 = (instr >> 27) & 0x1F
            if fmt == 0x1 and funct3 == 0x0:
                a = self._bits_to_double(self.fregs[rs1])
                b = self._bits_to_double(self.fregs[rs2])
                c = self._bits_to_double(self.fregs[rs3])
                res = a * b
                if opcode == 0x43:  # FMADD.D
                    res = res + c
                elif opcode == 0x47:  # FMSUB.D
                    res = res - c
                elif opcode == 0x4B:  # FNMSUB.D
                    res = -res - c
                else:  # 0x4F FNMADD.D
                    res = -res + c
                self.fregs[rd] = self._double_to_bits(res)
            else:
                self.last_exception = "illegal"
        elif opcode == 0x07 and funct3 == 0x0:  # Vector load (VLE64.V)
            imm = self._sign_extend(instr >> 20, 12)
            addr = (self.regs[rs1] + imm) & self.MASK64
            misalign = addr % 8 != 0
            if misalign:
                self.last_exception = "misalign"
            else:
                vec = 0
                for i in range(8):
                    pa = addr + i * 8
                    vec |= (self._mem_load(pa) & self.MASK64) << (64 * i)
                if self.last_exception is None:
                    self.vregs[rd] = vec & self.MASK512
        elif opcode == 0x07 and funct3 == 0x1:  # Gather load (VLUXEI64.V)
            scale = (instr >> 29) & 0x7
            vs2 = (instr >> 20) & 0x1F
            indices = [
                (self.vregs[vs2] >> (64 * i)) & self.MASK64 for i in range(8)
            ]
            vec = self.gather(self.regs[rs1], indices, scale)
            if self.last_exception is None:
                self.vregs[rd] = vec

        elif opcode == 0x27 and funct3 == 0x0:  # Vector store (VSE64.V)
            imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
            imm = self._sign_extend(imm, 12)
            addr = (self.regs[rs1] + imm) & self.MASK64
            misalign = addr % 8 != 0
            if misalign:
                self.last_exception = "misalign"
            else:
                for i in range(8):
                    pa = addr + i * 8
                    self._mem_store(pa, (self.vregs[rs2] >> (64 * i)) & self.MASK64)

        elif opcode == 0x27 and funct3 == 0x1:  # Scatter store (VSUXEI64.V)
            scale = (instr >> 29) & 0x7
            vs3 = (instr >> 20) & 0x1F
            vs2 = (instr >> 7) & 0x1F
            indices = [
                (self.vregs[vs2] >> (64 * i)) & self.MASK64 for i in range(8)
            ]
            self.scatter(self.regs[rs1], indices, scale, self.vregs[vs3])
        elif opcode == 0x57:  # Vector arithmetic
            funct6 = (instr >> 26) & 0x3F
            if funct6 == 0x00 and funct3 == 0x0:  # VADD.VV
                res = 0
                for i in range(8):
                    a = (self.vregs[rs1] >> (64 * i)) & self.MASK64
                    b = (self.vregs[rs2] >> (64 * i)) & self.MASK64
                    res |= ((a + b) & self.MASK64) << (64 * i)
                self.vregs[rd] = res
            elif funct6 == 0x01 and funct3 == 0x0:  # VFMA.VV (vd += vs1*vs2)
                res = 0
                for i in range(8):
                    a = (self.vregs[rs1] >> (64 * i)) & self.MASK64
                    b = (self.vregs[rs2] >> (64 * i)) & self.MASK64
                    c = (self.vregs[rd] >> (64 * i)) & self.MASK64
                    res |= ((a * b + c) & self.MASK64) << (64 * i)
                self.vregs[rd] = res
            elif funct6 == 0x02 and funct3 == 0x0:  # VMUL.VV
                res = 0
                for i in range(8):
                    a = (self.vregs[rs1] >> (64 * i)) & self.MASK64
                    b = (self.vregs[rs2] >> (64 * i)) & self.MASK64
                    res |= ((a * b) & self.MASK64) << (64 * i)
                self.vregs[rd] = res
            else:
                self.last_exception = "illegal"
        elif opcode == 0x2F:  # Atomic memory ops
            funct5 = (instr >> 27) & 0x1F
            aq    = (instr >> 26) & 1
            rl    = (instr >> 25) & 1
            addr = self.regs[rs1]
            if funct5 == 0x02:  # LR.D
                self.regs[rd] = self._mem_load(addr)
                self._reservation = addr
            elif funct5 == 0x03:  # SC.D
                if self._reservation == addr:
                    self._mem_store(addr, self.regs[rs2] & 0xFFFFFFFFFFFFFFFF)
                    self.regs[rd] = 0
                else:
                    self.regs[rd] = 1
                self._reservation = None
            elif funct5 == 0x00:  # AMOADD.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, (tmp + self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = tmp
            elif funct5 == 0x01:  # AMOSWAP.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, self.regs[rs2] & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = tmp
            elif funct5 == 0x04:  # AMOXOR.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, (tmp ^ self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = tmp
            elif funct5 == 0x08:  # AMOOR.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, (tmp | self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = tmp
            elif funct5 == 0x0C:  # AMOAND.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, (tmp & self.regs[rs2]) & 0xFFFFFFFFFFFFFFFF)
                self.regs[rd] = tmp
            elif funct5 == 0x10:  # AMOMIN.D
                tmp = self._mem_load(addr)
                a = tmp if tmp < 2**63 else tmp - 2**64
                b = self.regs[rs2] if self.regs[rs2] < 2**63 else self.regs[rs2] - 2**64
                self._mem_store(addr, tmp if a < b else self.regs[rs2])
                self.regs[rd] = tmp
            elif funct5 == 0x14:  # AMOMAX.D
                tmp = self._mem_load(addr)
                a = tmp if tmp < 2**63 else tmp - 2**64
                b = self.regs[rs2] if self.regs[rs2] < 2**63 else self.regs[rs2] - 2**64
                self._mem_store(addr, tmp if a > b else self.regs[rs2])
                self.regs[rd] = tmp
            elif funct5 == 0x18:  # AMOMINU.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, tmp if tmp < self.regs[rs2] else self.regs[rs2])
                self.regs[rd] = tmp
            elif funct5 == 0x1C:  # AMOMAXU.D
                tmp = self._mem_load(addr)
                self._mem_store(addr, tmp if tmp > self.regs[rs2] else self.regs[rs2])
                self.regs[rd] = tmp
        else:
            self.last_exception = "illegal"
        self.pc = next_pc
        return next_pc

    def execute_bundle(self, instructions):
        for instr in instructions:
            self.step(instr)
        return self.pc

    def _check_hazards(self, uops):
        """Return a list of data hazards within *uops*.

        Each entry is a dictionary ``{"type": str, "src": int, "dst": int, "reg": int}``
        describing the hazard type (``"RAW"``, ``"WAR"`` or ``"WAW"``), the index of
        the earlier instruction (``src``), the later conflicting instruction
        (``dst``) and the affected register number.
        """
        hazards = []
        writes = {}
        reads = {}
        for i, u in enumerate(uops):
            opcode = u["opcode"]
            rs = []
            use_rs1 = opcode not in (0x37, 0x17, 0x6F)
            use_rs2 = opcode in (0x33, 0x23, 0x63, 0x2F)
            if use_rs1 and u["rs1"]:
                rs.append(u["rs1"])
            if use_rs2 and u["rs2"]:
                rs.append(u["rs2"])
            for r in rs:
                reads.setdefault(r, []).append(i)
                if r in writes:
                    hazards.append({
                        "type": "RAW",
                        "src": writes[r],
                        "dst": i,
                        "reg": r,
                    })
            rd = u["rd"]
            if rd:
                if rd in writes:
                    hazards.append({
                        "type": "WAW",
                        "src": writes[rd],
                        "dst": i,
                        "reg": rd,
                    })
                for r_idx in reads.get(rd, []):
                    if r_idx < i:
                        hazards.append({
                            "type": "WAR",
                            "src": r_idx,
                            "dst": i,
                            "reg": rd,
                        })
                writes[rd] = i
        return hazards

    def issue_bundle(self, pc, instructions, *, coverage=None):
        """Decode and execute up to eight instructions starting at *pc*.

        Returns ``(uops, next_pc, hazards)`` where ``uops`` is the list of
        decoded micro-operations produced by :class:`Decoder8W`, ``next_pc`` is
        the program counter after executing the bundle and ``hazards`` lists any
        RAW/WAR/WAW hazards detected between the instructions.
        """
        self.pc = pc
        decoder = Decoder8W()
        uops = decoder.decode(instructions, coverage=coverage)
        hazards = self._check_hazards(uops)
        next_pc = self.execute_bundle(instructions)
        return uops, next_pc, hazards

    # ------------------------------------------------------------------
    # Vector gather/scatter helpers (not tied to a specific instruction)
    # ------------------------------------------------------------------
    def gather(self, base, indices, scale):
        """Return a 512-bit vector loaded using gather addressing."""

        self.last_exception = None
        step = 1 << scale
        result = 0
        for i in range(8):
            va = (base + indices[i] * step) & self.MASK64
            pa, fault = self.translate(va, 'r', override=self.smap_override)
            if va % step != 0:
                self.last_exception = "misalign"
                break
            if fault:
                self.last_exception = fault
                break
            if self._sev_addr(pa) not in self.mem:
                self.last_exception = "page"
                break
            lane = self._mem_load(pa) & self.MASK64
            result |= lane << (64 * i)
        return result & self.MASK512

    def scatter(self, base, indices, scale, data):
        """Store a 512-bit vector using scatter addressing."""

        self.last_exception = None
        step = 1 << scale
        for i in range(8):
            va = (base + indices[i] * step) & self.MASK64
            pa, fault = self.translate(va, 'w', override=self.smap_override)
            if va % step != 0:
                self.last_exception = "misalign"
                break
            if fault:
                self.last_exception = fault
                break
            if self._sev_addr(pa) not in self.mem:
                self.last_exception = "page"
                break
            lane = (data >> (64 * i)) & self.MASK64
            self._mem_store(pa, lane)
