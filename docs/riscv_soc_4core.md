# riscv_soc_4core Module

`riscv_soc_4core.sv` ties together four `core_tile_2smts_8wide` instances, L2 caches, the mesh interconnect and the DRAM model. This document only summarises the high level structure of the SoC; the current RTL is a placeholder without functional behavior.

A matching Python stub (`RiscvSoC4Core`) instantiates four
`CoreTile2SMT8Wide` objects and provides a `step()` method for tests.
