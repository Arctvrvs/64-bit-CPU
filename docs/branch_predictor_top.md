# branch_predictor_top Module

`branch_predictor_top.sv` implements a tiny branch prediction unit. It keeps a
small branch target buffer (BTB) indexed by bits of the program counter and a
2‑bit saturating counter per entry.

## Parameters

| Name | Default | Description |
|------|---------|-------------|
| `ENTRIES` | 32 | Number of BTB entries |

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `pc_i` | in | 64 | Program counter for lookup |
| `predicted_taken_o` | out | 1 | Predicted taken flag |
| `predicted_target_o` | out | 64 | Predicted target address |
| `update_valid_i` | in | 1 | Apply an update |
| `update_pc_i` | in | 64 | PC of executed branch |
| `update_taken_i` | in | 1 | Actual branch taken flag |
| `update_target_i` | in | 64 | Actual branch target |

## Behavior

On each cycle the predictor indexes its BTB using bits of `pc_i`. If the stored
tag matches, it outputs the saved target address and the high bit of the
counter as the taken prediction. When `update_valid_i` is asserted, the entry
indexed by `update_pc_i` is updated with the actual outcome and target and the
counter is incremented or decremented with saturation.
