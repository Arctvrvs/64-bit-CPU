# 64-bit RISC-V CPU Project

This repository contains an open source implementation of a high performance
64-bit RISC-V CPU. The design is organized by major functional blocks under the
`rtl/` directory with documentation in `docs/`.

Implemented modules so far:
- `golden_model` – minimal Python reference model
- `pc_fetch` – program counter generation for instruction fetch
- `l1_icache_64k_8w` – placeholder for the L1 instruction cache
- `if_buffer_16` – FIFO buffer between fetch and decode
- `decoder8w` – 8-wide instruction decoder placeholder
- `arch_regfile_32x64` – 32×64-bit architectural register file
- `phys_regfile_128x64` – 128×64-bit physical register file
- `rename_unit_8wide` – simple rename unit with free list
- `rob256` – reorder buffer placeholder
- `int_alu2` – dual one-cycle integer ALU pipelines
- `muldiv_unit` – pipelined multiply/divide unit
- `branch_unit` – resolves branches and detects mispredictions
- `amo_unit` – executes basic atomic operations

Development follows the tasks outlined in `docs/tasks/cpu.txt`.
