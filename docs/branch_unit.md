# branch_unit Module

The `branch_unit.sv` module resides in `rtl/ex_units/` and resolves both
conditional and unconditional branches in a single cycle.

## Parameters

This unit does not expose parameters beyond the standard interface.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `pc_ex_i` | in | 64 | Program counter at execute stage |
| `rs1_val_i` | in | 64 | First operand value |
| `rs2_val_i` | in | 64 | Second operand value |
| `branch_ctrl_i` | in | 3 | Branch type selector |
| `target_imm_i` | in | 32 | Sign-extended branch immediate |
| `predicted_taken_i` | in | 1 | Predictor taken flag |
| `predicted_target_i` | in | 64 | Predicted branch target |
| `actual_taken_o` | out | 1 | Actual taken result |
| `actual_target_o` | out | 64 | Actual branch target |
| `pred_mispredict_o` | out | 1 | High when prediction was incorrect |

## Behavior

Given operand values and a branch control code, the unit compares the
operands according to the branch type and produces an actual target
address. It also reports whether a misprediction occurred based on the
predicted inputs. All outputs are valid one cycle after the inputs.

A lightweight Python helper `BranchUnit` located in
`rtl/ex_units/branch_unit.py` mirrors this behavior for the unit tests.
