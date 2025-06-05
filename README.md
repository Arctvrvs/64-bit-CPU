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
- An improved branch predictor with a small counter-based BHT and BTB
  (`branch_predictor_advanced.v`)
- Multi-level cache hierarchy and MMU stubs
- Hooks for wide SIMD/vector execution units

These modules are currently minimal stubs intended to replace the older
pipelined core as more functionality is implemented.
The latest update adds a tiny instruction fetch queue used by
`cpu64_outoforder.v`.  This queue decouples fetching from the rename stage
so that future scheduling logic has a small buffer of instructions to
work with.

## Most Advanced CPU

A small wrapper module `cpu64_most_advanced.v` instantiates the experimental
out-of-order core. A corresponding testbench `tb_cpu64_most_advanced.v`
provides a simple clock and reset so that the design can be simulated.

To build and run the testbench with Icarus Verilog:

```sh
iverilog -o cpu64_tb Verilog/*.v
vvp cpu64_tb
```

The simulation will toggle the clock for a few hundred nanoseconds and
then finish, demonstrating that the advanced CPU integrates cleanly.

### Additional Features

The most advanced core now contains fleshed out support modules.
Several of the earlier placeholder components have been extended so the
out-of-order CPU can perform a little more useful work:

- `performance_counter.v` tracks cycles, retired instructions, memory
  accesses, branch events, cache misses and pipeline stalls.
- `debug_unit.v` prints each fetched instruction along with the current
  cycle count and notes cache misses, branch outcomes and stall status.
- `load_store_buffer.v` executes loads and stores out of order while
  enforcing program order commit and includes simple dependency and
  latency tracking.
- `fpu_unit.v` implements a tiny pipelined datapath with IEEE operations
  including conversions and fused multiply-add, plus basic exception
  reporting.
- `csr_unit.v` decodes CSR instructions, handles timer interrupts and
  updates privilege level with rudimentary checks.
- `issue_queue.v`, `reorder_buffer.v` and `register_rename.v` track
  dependencies for dozens of in-flight instructions and broadcast operand
  readiness.
- `cache_hierarchy.v` contains a two-level cache with a rudimentary LRU
  replacement policy while `mmu_unit.v` manages a larger TLB and reports
  faults on illegal accesses.
