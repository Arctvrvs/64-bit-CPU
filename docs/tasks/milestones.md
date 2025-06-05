# Implementation Milestones

This document provides a comprehensive list of tasks for implementing the 64-bit RISC-V CPU. Each milestone contains specific modules to develop, verification steps and directory placement.

## 1. Establish Foundations

1. **Create a RISC-V Golden Reference (C/Python Model)**
   * **Purpose:** Provide a cycle-agnostic, functional simulator (interpreter) of your chosen 64-bit RISC-V subset so that UVM testbenches can compare RTL results against expected behavior.
   * **Tasks:**
     1. Support the base integer ISA plus the required extensions:
        * RV64I (integer), RV64M (multiply/divide), RV64A (atomic), RV64F/ D? (floating-point), RV64V (vector).
        * Privileged spec (for MMU, page-table formats, exceptions).
        * 8-wide decode: permit up to 8 instructions per cycle in the golden model’s “issue stage.”
     2. Implement page-table walks and exception conditions (illegal instruction, page faults, misalign).
     3. Provide a clean API: given PC and up to 8 fetched instructions, return decoded µops, check hazards, update architectural state, and produce a next-PC.
   * **Verification:**
     * Run a suite of known RISC-V assembly tests (e.g., riscv-isa-sim test suite) to confirm correctness.
     * Provide a “reference trace” format (cycle by cycle µop retire, register writes, memory accesses).

2. **Set Up Code Repositories & Conventions**
   * **Directory Layout (exact):**
```
/rtl/
  /isa/
  /decode/
  /rf/
  /rename/
  /rob_rs_iq/
  /ex_units/
  /lsu/
  /bp/
  /cache/
  /mmu/
  /smt/
  /interconnect/
  /vm/
  /security/
  top.sv
/tb/
  /uvm_components/
  /tests/
Makefile
```
   * **Coding Style & Naming:**
     * Use consistent signal names (`clk`, `rst_n`, `opcode_i[6:0]`, `rs1_idx_i[4:0]`, `imm_i[31:0]`), module names (`decoder8w.sv`, `rob256.sv`, `cache_l1d_64k_8w.sv`).
     * Each module has a one-paragraph header (purpose, parameters, I/O summary).
     * Add attributes for clock-gating in modules where relevant (`(* clock_gating_cell = "yes" *)`).
   * **Simulation Tools:**
     * Use a SystemVerilog simulator (Questa/VCS) that supports UVM.
     * Lint with Verible or commercial lint.
     * Integrate code coverage (line, toggle, expression) and functional coverage points in UVM.

## 2. Instruction Fetch & Decode (Stages 1–3 of the 20)

1. **IF1 & IF2 Pipelines (Fetch from L1 I-Cache)**
   * **Module:** `pc_fetch.sv`
     * **Inputs:** `clk, rst_n, branch_taken, branch_target[63:0], flush_id`
     * **Outputs:** `pc_if2[63:0], pc_if1_plus8[63:0]`
     * **Behavior:**
       * On reset: `pc_reg = RESET_VECTOR`.
       * Else: if `branch_taken`, `pc_reg <= branch_target`; else `pc_reg <= pc_reg + 8`.
       * Provide `pc_if2 = pc_reg` and a lookahead `pc_if1_plus8 = pc_reg + 8`.
     * **Goal:** Drive two parallel I-cache requests each cycle.
   * **Module:** `l1_icache_64k_8w.sv`
     * **Params:** `LINE_BYTES=64`, `ASSOC=8`, `SETS=128`, `OFFSET_BITS=6`, `INDEX_BITS=7`, `TAG_BITS=51`.
     * **I/O:**
       * `input clk, rst_n, req_valid_if1, req_addr_if1[63:0], req_valid_if2, req_addr_if2[63:0]`
       * `output ready_if1, data_if1[63:0], ready_if2, data_if2[63:0]`
     * **Structure:**
       * Two tag lookups & two data reads per cycle.
       * On miss, allocate an MSHR entry (max 8 in flight).
       * Replacement via 7-bit pseudo-LRU per set.
   * **Module:** `if_buffer_16.sv` (Fetch FIFO)
     * Holds up to 16 instructions (128 bytes) to absorb I-cache latency.
     * Dequeues up to 8 bytes per cycle (two 32-bit instructions).
   * **Verification (per UVM):**
     * Write a UVM agent that drives `pc_fetch` and `l1_icache` with random aligned and misaligned fetches.
     * Cover cases: I-cache hits, misses, replacement, and MSHR contention.

2. **8-Wide Decoder (Stages 3–5)**
   * **Module:** `decoder8w.sv`
     * **Inputs:** Eight 32-bit instruction words (`instr0`…`instr7`) with `pc_i[63:0]`.
     * **Outputs:** For each µop `j` (0–7): `valid_j`, `rd_arch_j[4:0]`, `rs1_arch_j[4:0]`, `rs2_arch_j[4:0]`, `imm_j[63:0]`, `func3_j[2:0]`, `func7_j[6:0]`, `is_load_j`, `is_store_j`, `is_branch_j`, `is_alu_reg_j`, `is_alu_imm_j`, `is_fence_j`, `is_ecall_j`, `is_vector_j`, `is_priv_j`, `exception_j[2:0]`.
     * **Functionality:** Decode R-type, I-type, S-type, B-type, U-type, J-type, plus vector encoding (RVV). Generate a micro-op struct (`opcode_uop[6:0]`, `rs1_p[4:0]`, `rs2_p[4:0]`, `rd_p[4:0]`, `imm[63:0]`, `type_enum[3:0]`). Drive control signals for rename stage.
   * **Verification:**
     * UVM driver supplies random instruction words (including illegal encodings).
     * Scoreboard compares outputs to a golden decode model and checks coverage of all opcodes and immediate patterns.

## 3. Register File(s) & Rename (Stages 5–7)

1. **Architectural Register File (ARF) – 32 × 64-bit**
   * **Module:** `arch_regfile_32x64.sv`
     * **I/O:**
       * `clk, rst_n, we0, waddr0[4:0], wdata0[63:0]`
       * `raddr0[4:0], rdata0[63:0], raddr1[4:0], rdata1[63:0], raddr2[4:0], rdata2[63:0]`
     * **Behavior:** Write on `posedge clk` if `we0`; reads are asynchronous.
   * **Verification:** Write/read random patterns and check next-cycle behavior.
2. **Physical Register File (PRF) – 128 × 64-bit**
   * **Module:** `phys_regfile_128x64.sv`
     * **I/O:** Six read ports and four write ports with `clk` gating.
     * **Behavior:** Writes occur on `posedge clk` if `weX`; reads are asynchronous multiplexors across 128 entries.
   * **Verification:** Random read/write indices; check for read/write consistency under multi-port contention.
3. **Rename Table & Free-List – 32 Arch → 128 Phys**
   * **Module:** `rename_unit_8wide.sv`
     * **Inputs:** For each µop j (0..7) - `valid_in`, `rs1_arch_j`, `rs2_arch_j`, `rd_arch_j` plus ROB/RS availability and free list count.
     * **Outputs:** `rs1_phys_j`, `rs2_phys_j`, `rd_phys_j`, `old_rd_phys_j`, `rename_valid_j`.
     * **Internals:** `arch_to_phys`, free list FIFO, checkpoint stack.
     * **Recovery:** On branch mispredict, restore `arch_to_phys` and return unused phys regs.
   * **Verification:** UVM test drives random sequences; check mappings, free list count and checkpoint rollback.

## 4. Reorder Buffer, Reservation Stations, Issue Queue (Stages 7–10)

1. **Reorder Buffer (ROB) – 256 Entries**
   * **Module:** `rob256.sv`
     * **Allocate Port:** `rob_alloc_valid[j]`, `dest_phys_j`, `old_dest_phys_j`, `is_store_j`, `is_branch_j`, `is_exception_mpu_j` → returns `rob_idx_j` and `rob_alloc_ready`.
     * **Writeback Port:** `rob_wb_valid[k]`, `rob_wb_idx[k]`, `rob_wb_data[k]`, `rob_wb_exception[k]`.
     * **Commit Interface:** handshake signals with commit information.
     * **Internals:** Circular array with `head_ptr`, `tail_ptr`, `count`.
     * **Verification:** Scoreboard ensures commit order and proper resource freeing.
2. **Reservation Stations & Issue Queue – 128 Entries, 8-Way**
   * **Module:** `issue_queue_8wide.sv`
     * **Inputs:** dispatch signals, wakeup broadcasts, functional unit status.
     * **Outputs:** issue signals and stall indicator.
     * **Internals:** four RS arrays, wakeup buses, scheduling algorithm.
     * **Verification:** Random dependency sequences verifying readiness and issue width.

## 5. Execution Units (Stages 10–15)

1. **Integer ALUs (2 Pipes) & Multiply/Divide Unit**
   * **Module:** `int_alu2.sv`
   * **Module:** `muldiv_unit.sv`
   * **Verification:** Randomized arithmetic tests including overflow.
2. **Branch Unit (with Early Resolution in EX)**
   * **Module:** `branch_unit.sv`
   * **Verification:** Random branches to check target and mispredict detection.
3. **Load/Store Unit (LSU) – 2 Ports**
   * **Module:** `lsu.sv`
   * **Internals:** load queue, store buffer, memory ordering, vector support.
   * **Verification:** Random load/store with overlapping addresses and gather/scatter.
4. **Floating-Point / Vector Unit (512-bit AVX-Style)**
   * **Module:** `vector_fma512.sv`
   * **Verification:** Random vector operations with masking and FP corner cases.
5. **Integration of FUs**
   * **Module:** `ex_stage.sv`
   * **Verification:** Cross-check retired µop results with golden model.

## 6. Branch Predictor (Stages 3–8 in the Pipeline)

1. **Return Stack Buffer (RSB, 32 Entries)** – `rsb32.sv`
2. **Branch Target Buffer (BTB, 4096×8-way)** – `btb4096_8w.sv`
3. **TAGE Predictor (5 Tables, each 1024 Entries)** – `tage5.sv`
4. **Indirect Branch Predictor (IBP, 512×4-way)** – `ibp512_4w.sv`
5. **Branch Predictor Top-Level** – `branch_predictor_top.sv`
   * **Verification:** UVM tests with real branch traces checking 97% accuracy goal.

## 7. Multi-Level Cache Hierarchy & Coherence (Stages 15–18)

1. **L1 Data Cache – 64 KB, 8-way** – `l1_dcache_64k_8w.sv`
2. **L2 Cache – 1 MB, 8-way (Per Core)** – `l2_cache_1m_8w.sv`
3. **L3 Cache – 16 MB, 8-way (Shared Among 4 Cores)** – `l3_cache_16m_8w.sv`
4. **DRAM Model** – `dram_model.sv`
   * **Verification:** UVM sequences for hits, misses, eviction and coherence.

## 8. Full MMU (Stages 10–13)

1. **L1 TLBs – 64 entries, 8-way** – `tlb_l1_64e_8w.sv`
2. **L2 TLB – 512 entries, 8-way** – `tlb_l2_512e_8w.sv`
3. **Page Walker (Up to 8 In-Flight)** – `page_walker8.sv`
4. **Integration into LSU & I-Fetch**
   * **Verification:** Random VA loads/stores and fetches including large pages and permission faults.

## 9. SMT & Multi-Core Scalability (Stages 13–20)

1. **SMT Logic (2 Threads/Core)** – `smt_arbitration.sv`
2. **Core Tile** – `core_tile_2smts_8wide.sv`
3. **Interconnect & L3 Coherence (4-Core Chip; 2×2 Mesh)** – `router_5port.sv`, `l3_slice_4m_8w.sv`, `interconnect_mesh_2x2.sv`
4. **Top-Level (4-Core SoC)** – `riscv_soc_4core.sv`
   * **Verification:** Multi-core UVM tests with latency measurements and coherence corner cases.

## 10. Security & Virtualization (Optional Stubs)

1. **NX/SMEP/SMAP** – integrate permission checks in TLB and LSU.
2. **SGX Enclave Stubs** – `sgx_enclave.sv` with enclave management FSM.
3. **SEV Memory Encryption Stub** – per-VM key XOR before DRAM.
4. **Spectre/Meltdown Checks** – stall loads until TLB permissions confirmed and implement `SpecFetchFence` µop.
   * **Verification:** Directed UVM tests for each security feature.

## 11. UVM Verification Infrastructure

1. **Common UVM Components** – DVFS BFM, reset generator, memory models, coverage.
2. **Scoreboard & Reference Checker** – integrate golden model comparison at commit.
3. **Test Plans & Suites** – unit tests per stage, integration tests booting Linux, nightly regressions.

## 12. Final Checklist & Sign-Off

1. **Parameter Verification** – confirm widths, pipeline depth, caches, TLBs, vector lanes and predictor sizes.
2. **Deliverables** – RTL tree, UVM environment, golden model, documentation, Makefile/CI scripts.
3. **Milestones & Timeline** – months 1–12 tasks leading to final monolithic design.

