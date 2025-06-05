# pc_fetch Module

This document describes the `pc_fetch.sv` module implemented in the `rtl/fetch`
folder. The module generates program counter addresses for the instruction
fetch pipeline.

## Function

`pc_fetch` maintains the current PC and outputs two addresses each cycle to
allow fetching two instructions in parallel from the L1 instruction cache. It
handles branch redirection and supports a configurable reset vector.

## I/O Ports

| Name              | Dir   | Width | Description                              |
|-------------------|-------|-------|------------------------------------------|
| `clk`             | in    | 1     | Clock                                    |
| `rst_n`           | in    | 1     | Active-low reset                         |
| `branch_taken_i`  | in    | 1     | Redirect PC to `branch_target_i`         |
| `branch_target_i` | in    | 64    | Branch destination address               |
| `flush_id_i`      | in    | 4     | Reserved for future pipeline flush ID    |
| `pc_if2_o`        | out   | 64    | Current PC value                         |
| `pc_if1_plus8_o`  | out   | 64    | Next PC value (`PC + 8`)                 |

## Behavior

On reset the PC is initialized to `RESET_VECTOR`. Each cycle the PC either
updates to `branch_target_i` if a branch was taken or increments by eight bytes
to fetch the next pair of instructions.

