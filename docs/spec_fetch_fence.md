# spec_fetch_fence Module

`spec_fetch_fence.sv` implements a small helper for Spectre style speculation
mitigation. When a speculative fetch fence is inserted in the instruction
stream it prevents subsequent loads from completing until all earlier predicted
branches have retired.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `fence_i` | in | 1 | Assert to insert a pending fence |
| `retire_branch_i` | in | 1 | Branch retirement signal |
| `allow_load_o` | out | 1 | High when loads may proceed |

## Behavior

The module tracks a counter of outstanding fences. Each `fence_i` pulse
increments the counter, and each `retire_branch_i` pulse decrements it
if non-zero. `allow_load_o` is asserted only when no fences are pending.

A simple Python model is provided for unit tests.
