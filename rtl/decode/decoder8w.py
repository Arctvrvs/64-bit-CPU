class Decoder8W:
    """Very small decoder that extracts register fields and immediates"""

    @staticmethod
    def _sign_extend(val, bits):
        mask = 1 << (bits - 1)
        return (val & (mask - 1)) - (val & mask)

    def decode(self, instructions, coverage=None):
        """Decode a list of up to eight instruction words.

        When *coverage* is provided, opcodes and immediate values are recorded
        using the :class:`CoverageModel` interface.
        """
        results = []
        for instr in instructions:
            opcode = instr & 0x7F
            rd = (instr >> 7) & 0x1F
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1F
            rs2 = (instr >> 20) & 0x1F
            funct7 = (instr >> 25) & 0x7F
            imm = 0
            is_branch = opcode == 0x63 or opcode == 0x6F or opcode == 0x67
            is_load = opcode == 0x03
            is_store = opcode == 0x23

            if opcode in (0x13, 0x03, 0x67):
                imm = self._sign_extend(instr >> 20, 12)
            elif opcode == 0x23:
                imm = ((instr >> 7) & 0x1F) | (((instr >> 25) & 0x7F) << 5)
                imm = self._sign_extend(imm, 12)
            elif opcode == 0x63:
                imm = ((instr >> 7) & 0x1E) | ((instr >> 20) & 0x7E0)
                imm |= ((instr >> 7) & 0x1) << 11
                imm |= (instr >> 31) << 12
                imm = self._sign_extend(imm, 13)
            elif opcode == 0x6F:
                imm = ((instr >> 21) & 0x3FF) | ((instr >> 20) & 0x1) << 10
                imm |= ((instr >> 12) & 0xFF) << 11
                imm |= (instr >> 31) << 19
                imm = self._sign_extend(imm << 1, 21)

            if coverage:
                coverage.record_opcode(opcode)
                coverage.record_immediate(imm)

            results.append({
                "opcode": opcode,
                "rd": rd,
                "rs1": rs1,
                "rs2": rs2,
                "funct3": funct3,
                "funct7": funct7,
                "imm": imm,
                "is_branch": is_branch,
                "is_load": is_load,
                "is_store": is_store,
            })
        return results
