# 64-bit RISC-V CPU Project

This repository contains an open source implementation of a high performance
64-bit RISC-V CPU. The design is organized by major functional blocks under the
`rtl/` directory with documentation in `docs/`.

Implemented modules so far:
 - `golden_model` – minimal Python reference model with byte/half/word
   load/store support, SLT/SLTI ops, basic CSR instructions,
   floating-point add (`FADD.D`) and simple vector operations
   (`vle64.v`, `vse64.v`, `vadd.vv`)
   load/store support
- `pc_fetch` – program counter generation for instruction fetch
- `l1_icache_64k_8w` – placeholder for the L1 instruction cache with a small Python `L1ICache` model for tests
- `if_buffer_16` – FIFO buffer between fetch and decode with a Python `IFBuffer16` helper
- `decoder8w` – 8-wide instruction decoder placeholder with Python model
- `arch_regfile_32x64` – 32×64-bit architectural register file
- `phys_regfile_128x64` – 128×64-bit physical register file
- `csr_file` – simple control and status register block
- `rename_unit_8wide` – rename unit with free list and branch checkpoint stack
- `rob256` – reorder buffer placeholder
- `issue_queue_8wide` – small issue queue for early testing
- `int_alu2` – dual one-cycle integer ALU pipelines (Python model available)
- `muldiv_unit` – pipelined multiply/divide unit (Python model available)
- `branch_unit` – resolves branches and detects mispredictions (Python model available)
- `branch_predictor_top` – simple branch predictor with tiny BTB (Python model available)
- `rsb32` – return stack buffer for predicting RET targets
- `amo_unit` – executes basic atomic operations (Python model available)
 - `l1_dcache_64k_8w` – simple two-port data cache model with
    accompanying Python `L1DCache` helper
 - `lsu` – two-port load/store unit with Python `LSU` model and
    basic TLB/page-walker translation
- `tlb_l1_64e_8w` – small fully associative TLB
- `btb4096_8w` – basic branch target buffer
- `tage5` – simple multi-table TAGE predictor
- `ibp512_4w` – indirect branch predictor
- `vector_fma512` – placeholder vector FMA unit (Python model available)
 - `vector_lsu` – simplified vector load/store unit
 - `l2_cache_1m_8w` – stub L2 cache model with a Python `L2Cache` helper
- `tlb_l2_512e_8w` – level-2 TLB
- `page_walker` – simple page table walker
- `page_walker8` – multi-request page walker (Python model)
- `ex_stage` – wrapper that routes issued µops to functional units
- `smt_arbitration` – round-robin scheduler for SMT threads
- `router_5port` – simple five-port mesh router
- `l3_slice_4m_8w` – placeholder L3 cache slice
 - `l3_cache_16m_8w` – shared L3 cache (Python model)
- `directory_mesi` – simple MESI directory used by the L3 cache
- `nx_check` – no-execute permission checker
- `sgx_enclave` – minimal SGX enclave controller
- `sev_memory` – simple SEV memory encryption stub
- `spec_fetch_fence` – speculative load barrier for Spectre mitigation
- `smep_smap_check` – supervisor mode execute/access protection checker
- `vmcs` – virtualization control structure
- `ept` – extended page table translator
 - `interconnect_mesh_2x2` – wires four routers together (Python model)
 - `dram_model` – tiny backing memory model (Python `DRAMModel`)
- `instr_memory_model` – simple instruction memory backed by DRAMModel
- `data_memory_model` – simple data memory wrapper around DRAMModel
- `reset_generator` – helper producing an active-low reset pulse for tests
- `dvfs_bfm` – variable-frequency clock generator for DVFS testing
 - `scoreboard` – reference checker for retired instructions with
    per-cycle commit trace, reset capability, commit order checking via ROB
    indices, exception checking (illegal, misalign and page faults), optional
    load and store address/data verification, branch and prediction verification,
    optional coverage tracking (opcodes, exceptions and branch statistics),
    and ability to export the trace as CSV
- `coverage_model` – lightweight functional coverage tracker used in tests
- `regfile_bfm` – simple model that checks register file writes against
  the golden model
- `core_tile_2smts_8wide` – wrapper for two-thread core (Python model available)
- `riscv_soc_4core` – four-core SoC top (Python model available)
- `vmcs` – virtualization control structure
- `ept` – extended page table translator
- `interconnect_mesh_2x2` – wires four routers together
- `dram_model` – tiny backing memory model
- `instr_memory_model` – simple instruction memory backed by DRAMModel
- `data_memory_model` – simple data memory wrapper around DRAMModel
- `reset_generator` – helper producing an active-low reset pulse for tests
 - `scoreboard` – reference checker for retired instructions with
    per-cycle commit trace, reset capability, exception checking
    (illegal and misalign faults), optional load/store verification,
    branch and prediction verification, and ability to export the trace as CSV
- `regfile_bfm` – simple model that checks register file writes against
  the golden model
- `core_tile_2smts_8wide` – wrapper for two-thread core
- `riscv_soc_4core` – four-core SoC top

Development follows the tasks outlined in `docs/tasks/cpu.txt`.
