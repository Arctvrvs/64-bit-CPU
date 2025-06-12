# 64-bit RISC-V CPU Project

This repository contains an open source implementation of a high performance
64-bit RISC-V CPU. The design is organized by major functional blocks under the
`rtl/` directory with documentation in `docs/`.

Implemented modules so far:
 - `golden_model` – minimal Python reference model with byte/half/word
   load/store support, SLT/SLTI ops, basic CSR instructions,
  32-bit forms (`ADDW`, `SUBW`, `ADDIW`, `SLLIW`, `SRLIW`, `SRAIW`,
  `SLLW`, `SRLW`, `SRAW`) alongside floating-point add (`FADD.D`),
  subtract (`FSUB.D`), multiply (`FMUL.D`), divide (`FDIV.D`),
  min/max (`FMIN.D`/`FMAX.D`), fused multiply-add and
  subtract (`FMADD.D`, `FMSUB.D`, `FNMSUB.D`, `FNMADD.D`), simple vector operations
  (`vle64.v`, `vse64.v`, `vadd.vv`, `vmul.vv`, `vfma.vv`, `vluxei64.v`, `vsuxei64.v`) and
  gather/scatter helpers along with barrier and system instructions
  (`FENCE`, `FENCE.I`, `ECALL`, `EBREAK`).
  The helper
   `issue_bundle()` now reports basic RAW/WAR/WAW hazards in addition
   to returning the decoded µops and updated PC.
  When the built-in `VMCS` is enabled memory accesses are translated
  through the `EPT` stub for simple virtualization tests. The model also
  enforces NX/SMEP/SMAP protections when page table entries mark user pages
  or disable execute permission. An integrated `SGXEnclave` stub can
  restrict memory accesses while enclave mode is active and triggers a
  `"sgx"` exception on violations. A `SEVMemory` stub optionally encrypts
  memory accesses with a per-VM key so tests can verify AMD SEV style
  behavior. Loads normally enforce permissions before reading memory to
  model Meltdown protection, but this can be disabled with
  `set_meltdown_protect()` for experimentation.
  Address translation uses small L1 and L2 TLB helpers backed by a page
  walker model so coverage can track TLB hit/miss and walk events.
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
- `amo_unit` – executes atomic operations (add, swap, xor, or, and,
  min/max signed and unsigned) with a matching Python model
 - `l1_dcache_64k_8w` – simple two-port data cache model with
    accompanying Python `L1DCache` helper that can record cache hits and
    misses when given a `CoverageModel`
 - `lsu` – two-port load/store unit with Python `LSU` model and
    basic TLB/page-walker translation
- `tlb_l1_64e_8w` – small fully associative TLB
- `btb4096_8w` – basic branch target buffer
- `rsb32` – return stack buffer model that can log overflow/underflow events
- `tage5` – simple multi-table TAGE predictor
- `ibp512_4w` – indirect branch predictor
- `vector_fma512` – placeholder vector FMA unit (Python model available)
 - `vector_lsu` – simplified vector load/store unit with gather/scatter support
 - `l2_cache_1m_8w` – stub L2 cache model with a Python `L2Cache` helper
    that logs hits and misses if supplied with a coverage instance
 - `tlb_l2_512e_8w` – level-2 TLB
 - `page_walker` – simple page table walker that can record walk events when
   given a `CoverageModel`
 - `page_walker8` – multi-request page walker (Python model) with the same
   coverage hook
- `ex_stage` – wrapper that routes issued µops to functional units
- `smt_arbitration` – round-robin scheduler for SMT threads
- `router_5port` – simple five-port mesh router
- `l3_slice_4m_8w` – placeholder L3 cache slice
 - `l3_cache_16m_8w` – shared L3 cache (Python model) that can also
   record coverage statistics when provided with a `CoverageModel`
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
   optional coverage tracking (opcodes, exceptions, branch statistics and
   counters for vector loads/stores and gather/scatter operations),
   support for vector gather/scatter checks and ability to export the trace as
    CSV or JSON and dump a coverage summary as JSON. When virtualization is
    active the scoreboard automatically translates addresses through the EPT
    stub so load and store checks use host physical memory.
    ``dump_trace()`` returns the list of entries for convenience and the
    summary can also be obtained directly with ``get_coverage_summary()``.
    When no coverage model is attached the helper returns an empty dictionary.
    The resulting files can be parsed back with ``trace_utils.load_trace`` or
    ``trace_utils.load_trace_json``.
- `trace_utils` – helper functions to load or save reference traces in CSV or
  JSON format
- `coverage_model` – lightweight functional coverage tracker used in tests
  that can save and load summary reports via `save_summary()` and
  `load_summary()`
- `rsb32` also accepts a `CoverageModel` to log underflow/overflow events
- `regfile_bfm` – simple model that checks register file writes against
  the golden model
- `core_tile_2smts_8wide` – wrapper for two-thread core (Python model available)
- `riscv_soc_4core` – four-core SoC top (Python model available)
- `top` – thin wrapper that instantiates `riscv_soc_4core` (Python model available)
  and re-exported as `Top` from `tb.uvm_components` for convenience

Development follows the tasks outlined in `docs/tasks/cpu.txt`.

See `docs/verification_plan.md` for the current verification strategy and coverage goals.

## Running Tests

Execute `make test` to run the Python unit test suite. If the optional
`pytest-cov` package is installed the command will also produce a simple
coverage report on the console.
