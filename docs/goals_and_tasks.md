# 64-bit RISC-V CPU Project Goals and Tasks

This document captures the high level goals and a task breakdown for implementing
a high performance 64-bit RISC-V CPU. The design targets an 8-wide out-of-order
pipeline with full virtualization, vector extensions and UVM verification as
outlined in the planning document.

## Goals

1. **Complete RISC-V ISA Support** including integer, multiply/divide, atomic,
   floating point and vector extensions.
2. **20-Stage 8-Wide Superscalar Pipeline** capable of sustaining ~6 IPC at
   4–5 GHz.
3. **Simultaneous Multithreading** with two hardware threads per core sharing
   execution resources.
4. **Multi-level Caching and MMU** providing L1, L2 and L3 caches plus two level
   TLBs and page walker hardware.
5. **Security and Virtualization Stubs** for features such as SMEP, SMAP, SGX
   and SEV style memory encryption.
6. **UVM Based Verification** with a golden reference model for cycle accurate
   checking and coverage closure.

## Tasks Overview

The tasks closely follow the order described in the planning document and are
broken down into logical milestones. Each module should be developed in
SystemVerilog under `rtl/` and verified with UVM test benches under `tb/`.

### 1. Establish Foundations

- Create a cycle accurate RISC-V golden model in C or Python.
- Set up repository structure under `rtl/` and `tb/` with naming conventions.

### 2. Instruction Fetch & Decode

- Implement `pc_fetch.sv`, `l1_icache_64k_8w.sv` and supporting fetch buffer.
- Implement `decoder8w.sv` with full RV64 and vector decode.
- Verify with UVM agents generating aligned/misaligned fetches and opcode
  coverage.

### 3. Register File and Rename

- Create architectural and physical register files.
- Implement rename table with checkpoint and rollback support.
- Develop UVM tests for register hazards and branch misprediction recovery.

### 4. ROB, Reservation Stations and Issue

- Implement a 256 entry ROB with commit logic.
- Develop 128 entry issue queue with per functional unit reservation stations.
- Verify correct ordering and wakeup behaviour using randomized sequences.

### 5. Execution Units

- Implement integer ALUs, multiply/divide, branch unit, load/store unit and
  vector FMA pipeline.
- Build an execution stage wrapper that routes issued uops.
- Verify functional correctness of each unit vs. the golden model.

### 6. Branch Prediction

- Create return stack buffer, BTB, TAGE and indirect branch predictor.
- Integrate into a `branch_predictor_top` module driving the fetch stage.
- Measure prediction accuracy against traces.

### 7. Cache Hierarchy and Coherence

- Develop L1 data and instruction caches, L2 per-core caches and shared L3 with
  MESI directory using a mesh interconnect.
- Provide a simple DRAM model for misses.
- Verify multi-core coherency using UVM traffic generators.

### 8. MMU Implementation

- Implement L1 and L2 TLBs with a multi-entry page walker.
- Connect TLB lookups to LSU and instruction fetch.
- Test permission faults and large page support.

### 9. SMT and Multi-Core Integration

- Build SMT arbitration logic and a core tile combining two threads.
- Connect four cores through routers and L3 slices into a full SoC.
- Verify fairness between threads and coherence across cores.

### 10. Security Features and Virtualization

- Add stubs for SMEP/SMAP, SGX style enclaves and SEV memory encryption.
- Ensure speculative execution checks for Spectre/Meltdown mitigations.

### 11. UVM Infrastructure

- Create shared UVM components, scoreboard and coverage models.
- Automate regression tests and coverage reporting through the provided
  Makefile.

### 12. Documentation and Final Sign-Off

- Provide detailed interface specifications and architectural diagrams in the
  `docs/` directory.
- Track progress towards performance goals and verification coverage.
- Final deliverable is the complete SystemVerilog code base with passing UVM
  regression.
