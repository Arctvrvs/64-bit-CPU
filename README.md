# 64-bit CPU

This repository contains a simple 64-bit pipelined CPU written in Verilog. It
features basic arithmetic, logical operations and memory access instructions.

## Recent update

Shift instructions have been added using two new R-type function codes:

- `SLLV` (shift left logical variable)
- `SRLV` (shift right logical variable)

These operations correspond to new ALU op codes and allow the CPU to shift by a
variable amount specified in the second source register.

## Modern update

The pipeline now includes a `MUL` instruction using a new R-type function code
and ALU op. This multiplies two registers producing a 64-bit result.
