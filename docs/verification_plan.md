# Verification Plan

This document outlines the verification strategy for the 64-bit RISC-V CPU design. The goal is to achieve functional and code coverage closure using UVM testbenches backed by the Python golden reference model.

## Functional Coverage

- **Opcode coverage**: Track each unique opcode executed by the RTL. This is automatically collected by the `CoverageModel` via `record_opcode` when the scoreboard commits instructions.
- **Branch predictor events**: Allocation events for the BTB, TAGE and indirect branch predictor are recorded. Misprediction statistics are kept for all branch instructions.
- **Cache hierarchy**: Each cache level records hits and misses through `record_cache`. The L1 and L2 TLBs similarly log hits, misses and permission faults. Page walks are counted along with fault indicators.
- **RSB tracking**: Underflow and overflow of the return stack buffer are logged.
- **Exception coverage**: Illegal instruction, misalignment and page fault exceptions are tallied.

## Code Coverage

SystemVerilog simulations are run with coverage enabled so that line, toggle and expression metrics are produced. The Makefile invokes `run_tests.sh` which uses `pytest` and the optional `pytest-cov` plug‑in to gather Python coverage for the reference models and BFMs.

## Test Environment

Common UVM components reside under `tb/uvm_components`. The scoreboard instantiates the golden model and checks every retiring instruction. Memory models feed the caches and provide a consistent backing store. Tests are located in `tb/tests` and exercise individual blocks as well as full pipeline sequences. The `make test` target runs all Python tests. Each UVM testbench can be invoked separately when a SystemVerilog simulator is available.

## Regression

Nightly regression will execute the entire test suite and collect functional and code coverage results. Any drop in coverage or new failures will be flagged for investigation.
