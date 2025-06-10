// l1_dcache_64k_8w.sv - 64 KB 8-way set associative data cache (placeholder)
//
// Purpose: Provides a simple behavioral L1 D-cache model with two
// read/write ports. Each access completes in one cycle and is backed
// by an internal memory array. This module is a minimal stand-in for
// development and does not implement tags, replacement or miss logic.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module l1_dcache_64k_8w #(
    parameter int LINE_BYTES = 64,
    parameter int ASSOC      = 8,
    parameter int SETS       = 128
) (
    input  logic        clk,
    input  logic        rst_n,

    input  logic        req_valid_i[2],
    input  logic [63:0] req_addr_i[2],
    input  logic [63:0] req_wdata_i[2],
    input  logic [7:0]  req_wstrb_i[2],
    input  logic        req_is_write_i[2],

    output logic        rsp_ready_o[2],
    output logic [63:0] rsp_rdata_o[2]
);

    // Simple backing memory (64 KB)
    logic [63:0] mem [0:8191];

    // TLB translation (placeholder using simple combinational lookup)
    logic        tlb1_hit  [2];
    logic [63:0] tlb1_pa   [2];
    logic        tlb2_hit  [2];
    logic [63:0] tlb2_pa   [2];
    logic [63:0] phys_addr[2];

    for (genvar i = 0; i < 2; i++) begin : GEN_TLB
        tlb_l1_64e_8w u_tlb1 (
            .clk          (clk),
            .rst_n        (rst_n),
            .lookup_valid (req_valid_i[i]),
            .va_i         (req_addr_i[i]),
            .perm_req_i   (req_is_write_i[i] ? 3'b010 : 3'b001),
            .hit_o        (tlb1_hit[i]),
            .pa_o         (tlb1_pa[i]),
            .perm_fault_o (),
            .refill_valid (1'b0),
            .refill_va_i  (64'd0),
            .refill_pa_i  (64'd0),
            .refill_perm_i(3'b0)
        );

        tlb_l2_512e_8w u_tlb2 (
            .clk            (clk),
            .rst_n          (rst_n),
            .req_valid_i    (~tlb1_hit[i] & req_valid_i[i]),
            .req_vaddr_i    (req_addr_i[i]),
            .req_perm_i     (req_is_write_i[i] ? 3'b010 : 3'b001),
            .hit_o          (tlb2_hit[i]),
            .resp_paddr_o   (tlb2_pa[i]),
            .fault_o        (),
            .refill_valid_i (1'b0),
            .refill_vaddr_i (64'd0),
            .refill_paddr_i (64'd0),
            .refill_perm_i  (3'b0)
        );

        always_comb begin
            if (tlb1_hit[i])
                phys_addr[i] = tlb1_pa[i];
            else if (tlb2_hit[i])
                phys_addr[i] = tlb2_pa[i];
            else
                phys_addr[i] = req_addr_i[i];
        end
    end

    // Requests complete in one cycle using the translated address
    always_ff @(posedge clk) begin
        for (int i = 0; i < 2; i++) begin
            if (req_valid_i[i]) begin
                if (req_is_write_i[i]) begin
                    for (int b = 0; b < 8; b++) begin
                        if (req_wstrb_i[i][b])
                            mem[phys_addr[i][15:3]][8*b +: 8] <= req_wdata_i[i][8*b +: 8];
                    end
                end else begin
                    rsp_rdata_o[i] <= mem[phys_addr[i][15:3]];
                end
            end
        end
    end

    assign rsp_ready_o[0] = req_valid_i[0];
    assign rsp_ready_o[1] = req_valid_i[1];

endmodule
