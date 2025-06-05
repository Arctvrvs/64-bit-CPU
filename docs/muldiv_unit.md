# muldiv_unit Module

`muldiv_unit.sv` provides hardware support for RV64M multiplication and division
operations. Multiplication is performed in a three stage pipeline while division
uses an iterative algorithm that completes in twenty cycles. The unit tracks the
destination physical register and ROB index so that results may be written back
out-of-order.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `valid_i` | in | 1 | Operation valid |
| `op_a_i` | in | 64 | Operand A |
| `op_b_i` | in | 64 | Operand B |
| `md_ctrl_i` | in | 3 | Multiply/divide selector |
| `dest_phys_i` | in | 7 | Destination physical register |
| `rob_idx_i` | in | 8 | ROB index |
| `ready_o` | out | 1 | Result valid |
| `result_o` | out | 64 | Result value |
| `dest_phys_o` | out | 7 | Destination physical register |
| `rob_idx_o` | out | 8 | ROB index |

## Behavior

Multiplications take three cycles using a small pipeline. Divisions are
iterative and finish after twenty cycles. When a result becomes available the
unit raises `ready_o` along with the associated bookkeeping fields so that the
ROB can mark the entry complete.
