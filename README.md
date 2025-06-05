# 64-bit CPU

This repository contains a simple 64-bit pipelined CPU written in Verilog. It
features basic arithmetic, logical operations and memory access instructions.

## Recent update

Shift instructions have been added using two new R-type function codes:

- `SLLV` (shift left logical variable)
- `SRLV` (shift right logical variable)

These operations correspond to new ALU op codes and allow the CPU to shift by a
variable amount specified in the second source register.

## Superscalar Version

A new experimental module `cpu64_superscalar.v` demonstrates a dual-issue pipeline. It fetches and decodes two instructions per cycle and uses a shared register file with four read ports. Minimal cross-lane hazard detection is provided via `hazard_unit_superscalar.v`.
