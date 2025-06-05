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

## Out-of-Order Version

The file `cpu64_outoforder.v` sketches the next evolution of the design. It
incorporates building blocks for:

- Out-of-order issue using a simple issue queue and reorder buffer
- Register renaming to eliminate false dependencies
- A placeholder high-accuracy branch predictor (`branch_predictor_advanced.v`)
- Multi-level cache hierarchy and MMU stubs
- Hooks for wide SIMD/vector execution units

These modules are currently minimal stubs intended to replace the older
pipelined core as more functionality is implemented.
