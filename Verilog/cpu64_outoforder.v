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
    wire fq_dequeue;
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

    // ----- Decode and register renaming -----
    wire [31:0] instr_fetch;
    wire [5:0] phys_src1, phys_src2, phys_dest;

    register_rename rename_u(
        .clk(clk),
        .rst_n(rst_n),
        .decode_instr(instr_fetch),
        .rename_ready(rename_ready),
        .phys_src1(phys_src1),
        .phys_src2(phys_src2),
        .phys_dest(phys_dest)
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
        .ready(issue_ready)
    );

    // ----- Reorder buffer and execution units -----
    wire commit_ready;
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

    // ----- Memory hierarchy -----
    wire [63:0] mem_addr, mem_write_data, mem_read_data;
    cache_hierarchy cache_u(
        .clk(clk),
        .rst_n(rst_n),
        .mem_read(1'b0),
        .mem_write(1'b0),
        .addr(mem_addr),
        .write_data(mem_write_data),
        .read_data(mem_read_data)
    );

    // MMU stub
    mmu_unit mmu_u(
        .clk(clk),
        .rst_n(rst_n),
        .virt_addr(mem_addr),
        .phys_addr()
    );
endmodule
