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
- `issue_queue_8wide` – small issue queue for early testing
- `int_alu2` – dual one-cycle integer ALU pipelines
- `muldiv_unit` – pipelined multiply/divide unit
- `branch_unit` – resolves branches and detects mispredictions
- `branch_predictor_top` – simple branch predictor with tiny BTB
- `rsb32` – return stack buffer for predicting RET targets
- `amo_unit` – executes basic atomic operations
- `l1_dcache_64k_8w` – simple two-port data cache model
- `lsu` – two-port load/store unit
- `tlb_l1_64e_8w` – small fully associative TLB
- `btb4096_8w` – basic branch target buffer
- `tage5` – simple multi-table TAGE predictor
- `ibp512_4w` – indirect branch predictor
- `vector_fma512` – placeholder vector FMA unit
- `l2_cache_1m_8w` – stub L2 cache model
- `tlb_l2_512e_8w` – level-2 TLB
- `page_walker` – simple page table walker
- `ex_stage` – wrapper that routes issued µops to functional units
- `smt_arbitration` – round-robin scheduler for SMT threads
- `router_5port` – simple five-port mesh router
- `l3_slice_4m_8w` – placeholder L3 cache slice
- `nx_check` – no-execute permission checker
- `vmcs` – virtualization control structure
- `ept` – extended page table translator
- `interconnect_mesh_2x2` – wires four routers together
- `dram_model` – tiny backing memory model
- `core_tile_2smts_8wide` – wrapper for two-thread core
- `riscv_soc_4core` – four-core SoC top

Development follows the tasks outlined in `docs/tasks/cpu.txt`.
