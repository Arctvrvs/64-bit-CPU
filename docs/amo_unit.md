# amo_unit Module

`amo_unit.sv` resides in `rtl/ex_units/` and executes atomic memory
operations from the RV64A extension. The unit is a placeholder that
performs the arithmetic portion of AMOs and relies on the load/store
unit to handle memory ordering.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `valid_i` | in | 1 | Operation valid |
| `op_a_i` | in | 64 | Value loaded from memory |
| `op_b_i` | in | 64 | Register operand |
| `amo_funct_i` | in | 3 | AMO function code |
| `result_o` | out | 64 | Computed result |
| `ready_o` | out | 1 | Result valid |

## Behavior

Given the loaded value and register operand, the unit performs the
specified operation (swap or add currently) and outputs the result on
the next cycle. The design is intentionally simple for early
integration tests.
A lightweight Python helper `AmoUnit` mirrors the RTL for unit tests.
