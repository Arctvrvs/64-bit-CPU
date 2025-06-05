# 64-bit RISC-V CPU Project

This repository contains an open source implementation of a high performance
64-bit RISC-V CPU. The design is organized by major functional blocks under the
`rtl/` directory with documentation in `docs/`.

Implemented modules so far:
- `pc_fetch` – program counter generation for instruction fetch
- `l1_icache_64k_8w` – placeholder for the L1 instruction cache
- `if_buffer_16` – FIFO buffer between fetch and decode
- `decoder8w` – 8-wide instruction decoder placeholder

Development follows the tasks outlined in `docs/tasks/cpu.txt`.
