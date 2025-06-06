# decoder8w Module

This document describes the `decoder8w.sv` module which decodes up to eight instructions per cycle. The decoder translates 32-bit RISC-V instruction words into micro-ops used by downstream rename and issue stages.

## Function

`decoder8w` accepts eight instruction words accompanied by their program counters. For each instruction it outputs decoded register indices, immediate values and type information. This initial version supports a minimal subset of RV64I required for early testing.

A small Python helper class `Decoder8W` mirrors the RTL decoder. It
extracts the same register fields and immediates so unit tests can verify
decode results without running a simulator.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `instr_i[7:0]` | in | 32 each | Instruction words to decode |
| `pc_i[7:0]` | in | 64 each | Program counter of each instruction |
| `valid_o[7:0]` | out | 1 each | Instruction decode valid |
| `rd_arch_o[7:0][4:0]` | out | 5 each | Destination architectural register |
| `rs1_arch_o[7:0][4:0]` | out | 5 each | Source register 1 |
| `rs2_arch_o[7:0][4:0]` | out | 5 each | Source register 2 |
| `imm_o[7:0][63:0]` | out | 64 each | Immediate value |
| `func3_o[7:0][2:0]` | out | 3 each | Function 3 field |
| `func7_o[7:0][6:0]` | out | 7 each | Function 7 field |
| `is_branch_o[7:0]` | out | 1 each | Branch instruction flag |
| `exception_o[7:0][2:0]` | out | 3 each | Decode exception bits |

The micro-op structure will be refined as additional instructions are supported.
