# branch_predictor_top Module

`branch_predictor_top.sv` integrates several prediction structures: a return
stack buffer (RSB), a branch target buffer (BTB) with 2‑bit saturating
counters, a small TAGE predictor and an indirect branch predictor. The module
selects the next PC based on decode information and updates predictor state when
branches retire.


## Parameters

| Name | Default | Description |
|------|---------|-------------|
| `ENTRIES` | 32 | Number of BTB entries |

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `pc_id_i` | in | 64 | Program counter from ID stage |
| `is_call_i` | in | 1 | Instruction is CALL |
| `is_ret_i` | in | 1 | Instruction is RET |
| `is_cond_branch_i` | in | 1 | Instruction is conditional branch |
| `is_uncond_branch_i` | in | 1 | Instruction is unconditional branch |
| `is_indirect_i` | in | 1 | Instruction is indirect branch |
| `last_target_i` | in | 64 | Previous target for IBP hashing |
| `pred_taken_o` | out | 1 | Predicted taken flag |
| `predicted_pc_o` | out | 64 | Predicted next PC |
| `update_valid_i` | in | 1 | Apply an update |
| `pc_retire_i` | in | 64 | PC of retiring branch |
| `actual_taken_i` | in | 1 | Actual branch taken flag |
| `actual_target_i` | in | 64 | Actual branch target |
| `is_branch_retire_i` | in | 1 | Retiring instruction was a branch |
| `is_indirect_retire_i` | in | 1 | Retiring instruction was indirect |

## Behavior

The predictor chooses the next PC using the following priority:

1. If `is_ret_i` is asserted, the return stack buffer provides the predicted
   address.
2. Else if `is_uncond_branch_i` is set, the BTB supplies the target address.
3. Else if `is_cond_branch_i` is set, the TAGE predictor decides whether the
   branch is taken. If taken, the BTB target is used.
4. Else if `is_indirect_i` is set, the indirect branch predictor returns the
   predicted target address.
5. Otherwise the next sequential PC (`pc_id_i + 4`) is chosen.

On branch retirement the BTB, TAGE and IBP tables are updated with the actual
outcome and target. Calls push the return address onto the RSB and returns pop
it.

