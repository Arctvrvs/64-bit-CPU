# Modern 64-bit CPU Design

This directory collects high-level design notes for a more advanced 64-bit CPU. The goal is to evolve the existing simple core into a modern processor with features comparable to today\'s desktop and server CPUs.

## Key Features

- **Superscalar, deep pipelining** – multiple instructions executed per cycle over many pipeline stages.
- **Out-of-order execution and register renaming** – issue logic selects ready instructions while avoiding false dependencies.
- **Highly accurate branch prediction** including TAGE predictors, return stack buffer (RSB) and branch target buffers (BTB).
- **Multi-level cache hierarchy** with L1, L2 and shared L3 caches using sophisticated replacement strategies.
- **Wide SIMD/vector units** supporting AVX‑512 and Fused Multiply‑Add (FMA).
- **Multi-core with SMT** – for example up to 16 cores each supporting two hardware threads.
- **MMU with multi-level TLB** and a hardware page walker for virtual memory.
- **Hardware virtualization** features like Intel VT‑x or AMD‑V.
- **Security extensions** such as NX, SMEP, SMAP, SGX/SEV and mitigations for Meltdown/Spectre.
- **Integrated memory and PCIe controllers** plus high-bandwidth interconnect (InfinityFabric or QuickPath).
- **Power management** with dynamic voltage/frequency scaling, clock gating and on-die voltage regulation.
- **Extensive verification** using UVM and formal methods alongside physical design targeting advanced nodes (e.g. 7 nm or 5 nm).

These notes serve as a starting point for documenting modules, microarchitecture diagrams and further exploration as development proceeds.
