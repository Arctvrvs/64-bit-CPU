# tage5 Module

The `tage5.sv` module implements a highly simplified TAGE branch predictor. It
contains five tables of 1024 entries each. Every entry stores a 2‑bit
saturating counter. Tables are indexed by a hash of the program counter and a
small global history shift register.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `pc_i` | in | 64 | Program counter for prediction |
| `pred_taken_o` | out | 1 | Predicted taken flag |
| `update_valid_i` | in | 1 | Update enable |
| `update_pc_i` | in | 64 | PC of retired branch |
| `update_taken_i` | in | 1 | Actual taken flag |

## Behavior

On each prediction request the module hashes `pc_i` with the current history for
each table and sums the high bits of the selected counters. If the sum exceeds
half the number of tables it predicts the branch as taken. Updates increment or
decrement the counters and shift the history register.
