# int_alu2 Module

`int_alu2.sv` implements a pair of simple 64‑bit integer ALU pipelines. Each
pipeline accepts operands and an operation code and returns the result one cycle
later along with destination bookkeeping fields. The unit is used to execute
standard RV64I ALU instructions in a single cycle.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `valid0_i` | in | 1 | Pipeline 0 operation valid |
| `op1_0_i` | in | 64 | Operand 1 pipe 0 |
| `op2_0_i` | in | 64 | Operand 2 pipe 0 |
| `alu_ctrl_0_i` | in | 4 | ALU control pipe 0 |
| `dest_phys_0_i` | in | 7 | Destination physical reg pipe 0 |
| `rob_idx_0_i` | in | 8 | ROB index pipe 0 |
| `valid1_i` | in | 1 | Pipeline 1 operation valid |
| `op1_1_i` | in | 64 | Operand 1 pipe 1 |
| `op2_1_i` | in | 64 | Operand 2 pipe 1 |
| `alu_ctrl_1_i` | in | 4 | ALU control pipe 1 |
| `dest_phys_1_i` | in | 7 | Destination physical reg pipe 1 |
| `rob_idx_1_i` | in | 8 | ROB index pipe 1 |
| `valid0_o` | out | 1 | Result valid pipe 0 |
| `result_0_o` | out | 64 | Result pipe 0 |
| `dest_phys_0_o` | out | 7 | Destination physical reg pipe 0 |
| `rob_idx_0_o` | out | 8 | ROB index pipe 0 |
| `valid1_o` | out | 1 | Result valid pipe 1 |
| `result_1_o` | out | 64 | Result pipe 1 |
| `dest_phys_1_o` | out | 7 | Destination physical reg pipe 1 |
| `rob_idx_1_o` | out | 8 | ROB index pipe 1 |

## Behavior

The ALUs perform standard arithmetic, logical and shift operations. Both
pipelines operate independently allowing two instructions per cycle. Results are
latched on the rising clock edge and forwarded to the write‑back network.

A lightweight Python model (`IntALU2`) mirrors the RTL for unit testing. It executes two operations per call and returns result dictionaries for verification.
