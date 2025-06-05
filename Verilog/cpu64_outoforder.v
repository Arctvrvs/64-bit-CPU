// cpu64_outoforder.v
// Experimental out-of-order superscalar CPU skeleton.
// This file outlines a future direction for the design including
// register renaming, advanced branch prediction and multi-level caches.

`timescale 1ns/1ps
module cpu64_outoforder(
    input  wire clk,
    input  wire rst_n
);
    // --------------------------------------------------------------
    //  Fetch stage with branch prediction and a small fetch queue
    // --------------------------------------------------------------
    reg  [63:0] pc_reg;
    wire [63:0] fetch_pc;
    wire        bp_taken;
    wire [63:0] bp_target;
    wire        rename_ready;  // declared early for fetch queue logic
    wire        fq_empty, fq_full;
    wire        fq_dequeue;    // also used by debug unit

    // Branch predictor uses the current fetch PC
    branch_predictor_advanced bp_u(
        .clk           (clk),
        .rst_n         (rst_n),
        .pc_fetch      (pc_reg),
        .predict_taken (bp_taken),
        .predict_target(bp_target),
        .update_valid  (1'b0),
        .update_pc     (64'b0),
        .update_taken  (1'b0),
        .update_target (64'b0)
    );

    // Advance the PC when the queue can accept more instructions
    assign fq_dequeue = rename_ready && !fq_empty;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc_reg <= 64'b0;
        end else if (!fq_full) begin
            pc_reg <= bp_taken ? bp_target : pc_reg + 64'd4;
        end
    end

    fetch_queue fq_u(
        .clk    (clk),
        .rst_n  (rst_n),
        .pc_in  (pc_reg),
        .dequeue(fq_dequeue),
        .pc_out (fetch_pc),
        .instr_out(instr_fetch),
        .empty  (fq_empty),
        .full   (fq_full)
    );

    // Debug unit prints the PC and instruction as they are dequeued
    debug_unit dbg_u(
        .clk   (clk),
        .rst_n (rst_n),
        .pc    (fetch_pc),
        .instr (instr_fetch),
        .cycle (cycle_count),
        .valid (fq_dequeue),
        .cache_miss(cache_miss),
        .branch_taken(bp_taken),
        .stall(1'b0)
    );

    // ----- Decode and register renaming -----
    wire [31:0] instr_fetch;
    wire [5:0] phys_src1, phys_src2, phys_dest;
    wire        commit_ready;

    register_rename rename_u(
        .clk(clk),
        .rst_n(rst_n),
        .decode_instr(instr_fetch),
        .rename_ready(rename_ready),
        .phys_src1(phys_src1),
        .phys_src2(phys_src2),
        .phys_dest(phys_dest),
        .commit_valid(commit_ready),
        .commit_phys(phys_dest)
    );

    // ----- Issue queue -----
    wire issue_ready;
    issue_queue issue_u(
        .clk(clk),
        .rst_n(rst_n),
        .instr(instr_fetch),
        .phys_src1(phys_src1),
        .phys_src2(phys_src2),
        .phys_dest(phys_dest),
        .wakeup_valid(1'b0),
        .wakeup_phys(6'b0),
        .ready(issue_ready)
    );

    // ----- Reorder buffer and execution units -----
    reorder_buffer rob_u(
        .clk(clk),
        .rst_n(rst_n),
        .issue_ready(issue_ready),
        .commit_ready(commit_ready)
    );

    vector_unit vec_u(
        .clk(clk),
        .rst_n(rst_n),
        .issue_ready(issue_ready),
        .commit_ready()
    );

    // Floating point and CSR units demonstrate simple execution
    fpu_unit fpu_u(
        .clk        (clk),
        .rst_n      (rst_n),
        .issue_valid(issue_ready),
        .opcode     (3'd0),
        .src1       (64'h3ff0000000000000),
        .src2       (64'h4000000000000000),
        .src3       (64'h0),
        .commit_ready(),
        .result(),
        .invalid(),
        .overflow(),
        .underflow(),
        .inexact(),
        .div_by_zero()
    );

    csr_unit csr_u(
        .clk        (clk),
        .rst_n      (rst_n),
        .issue_valid(issue_ready),
        .csr_op     (3'd0),
        .csr_addr   (12'h305),
        .write_data (64'h0),
        .commit_ready(),
        .read_data(),
        .priv_level(),
        .illegal_access()
    );

    // ----- Memory hierarchy -----
    wire        mem_read, mem_write;
    wire [63:0] mem_addr, mem_write_data, mem_read_data;
    wire        cache_miss;

    load_store_buffer lsb_u(
        .clk         (clk),
        .rst_n       (rst_n),
        .issue_valid (issue_ready),
        .is_store    (1'b0),
        .addr_in     (64'h1000),
        .data_in     (64'hDEADBEEF),
        .commit_ready(),
        .mem_read    (mem_read),
        .mem_write   (mem_write),
        .mem_addr    (mem_addr),
        .write_data  (mem_write_data),
        .read_data   (mem_read_data),
        .miss        (cache_miss)
    );

    cache_hierarchy cache_u(
        .clk       (clk),
        .rst_n     (rst_n),
        .mem_read  (mem_read),
        .mem_write (mem_write),
        .addr      (mem_addr),
        .write_data(mem_write_data),
        .read_data (mem_read_data),
        .miss      (cache_miss)
    );

    // MMU stub
    mmu_unit mmu_u(
        .clk(clk),
        .rst_n(rst_n),
        .virt_addr(mem_addr),
        .access_write(mem_write),
        .phys_addr(),
        .fault()
    );

    // Performance counters for profiling
    wire [63:0] cycle_count, instr_count, mem_count;
    performance_counter perf_u(
        .clk           (clk),
        .rst_n         (rst_n),
        .instr_valid   (issue_ready),
        .mem_valid     (mem_read | mem_write),
        .bp_miss       (1'b0),
        .branch_taken  (bp_taken),
        .cache_miss    (cache_miss),
        .stall         (1'b0),
        .flush         (1'b0),
        .cycle_count   (cycle_count),
        .instr_count   (instr_count),
        .mem_count     (mem_count),
        .bp_miss_count (),
        .cache_miss_count(),
        .stall_count   (),
        .flush_count   (),
        .branch_count  ()
    );
endmodule
