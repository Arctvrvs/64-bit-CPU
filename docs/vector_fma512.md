# vector_fma512 Module

`vector_fma512.sv` implements a simplified 512‑bit fused multiply-add unit. It
accepts three 512‑bit operands and produces the result after five cycles.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `valid_i` | in | 1 | Input valid |
| `src1_i` | in | 512 | First operand |
| `src2_i` | in | 512 | Second operand |
| `src3_i` | in | 512 | Addend |
| `valid_o` | out | 1 | Result valid |
| `result_o` | out | 512 | FMA result |

## Behavior

When `valid_i` is asserted the module multiplies `src1_i` and `src2_i`, adds
`src3_i` and outputs the result five cycles later. This model treats the entire
512‑bit vector as a large integer for simplicity.
