// l1_icache_64k_8w.sv - 64 KB 8-way set associative instruction cache
//
// Purpose: Supplies two 64-bit instruction words per cycle to the fetch
// pipeline. Supports two independent read ports and tracks misses via
// a small MSHR. This is a behavioral placeholder model.

module l1_icache_64k_8w #(
    parameter int LINE_BYTES  = 64,
    parameter int ASSOC       = 8,
    parameter int SETS        = 128,
    parameter int OFFSET_BITS = 6,
    parameter int INDEX_BITS  = 7,
    parameter int TAG_BITS    = 51
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_if1,
    input  logic [63:0] req_addr_if1,
    input  logic        req_valid_if2,
    input  logic [63:0] req_addr_if2,
    output logic        ready_if1,
    output logic [63:0] data_if1,
    output logic        ready_if2,
    output logic [63:0] data_if2,
    output logic [63:0] miss_addr_if1,
    output logic [63:0] miss_addr_if2
);

    // Simple placeholder arrays for tags and data
    logic [TAG_BITS-1:0] tags [SETS-1:0][ASSOC-1:0];
    logic [63:0]         data_mem [SETS-1:0][ASSOC-1:0];

    // TLB translation for both fetch addresses
    logic        tlb1_hit [2];
    logic [63:0] tlb1_pa  [2];
    logic        tlb2_hit [2];
    logic [63:0] tlb2_pa  [2];
    logic [63:0] phys_addr[2];

    tlb_l1_64e_8w itlb1 (
        .clk          (clk),
        .rst_n        (rst_n),
        .lookup_valid (req_valid_if1),
        .va_i         (req_addr_if1),
        .perm_req_i   (3'b100),
        .hit_o        (tlb1_hit[0]),
        .pa_o         (tlb1_pa[0]),
        .perm_fault_o (),
        .refill_valid (1'b0),
        .refill_va_i  (64'd0),
        .refill_pa_i  (64'd0),
        .refill_perm_i(3'b0)
    );

    tlb_l1_64e_8w itlb1_b (
        .clk          (clk),
        .rst_n        (rst_n),
        .lookup_valid (req_valid_if2),
        .va_i         (req_addr_if2),
        .perm_req_i   (3'b100),
        .hit_o        (tlb1_hit[1]),
        .pa_o         (tlb1_pa[1]),
        .perm_fault_o (),
        .refill_valid (1'b0),
        .refill_va_i  (64'd0),
        .refill_pa_i  (64'd0),
        .refill_perm_i(3'b0)
    );

    tlb_l2_512e_8w itlb2 (
        .clk            (clk),
        .rst_n          (rst_n),
        .req_valid_i    (~tlb1_hit[0] & req_valid_if1),
        .req_vaddr_i    (req_addr_if1),
        .req_perm_i     (3'b100),
        .hit_o          (tlb2_hit[0]),
        .resp_paddr_o   (tlb2_pa[0]),
        .fault_o        (),
        .refill_valid_i (1'b0),
        .refill_vaddr_i (64'd0),
        .refill_paddr_i (64'd0),
        .refill_perm_i  (3'b0)
    );

    tlb_l2_512e_8w itlb2_b (
        .clk            (clk),
        .rst_n          (rst_n),
        .req_valid_i    (~tlb1_hit[1] & req_valid_if2),
        .req_vaddr_i    (req_addr_if2),
        .req_perm_i     (3'b100),
        .hit_o          (tlb2_hit[1]),
        .resp_paddr_o   (tlb2_pa[1]),
        .fault_o        (),
        .refill_valid_i (1'b0),
        .refill_vaddr_i (64'd0),
        .refill_paddr_i (64'd0),
        .refill_perm_i  (3'b0)
    );

    always_comb begin
        phys_addr[0] = tlb1_hit[0] ? tlb1_pa[0] : (tlb2_hit[0] ? tlb2_pa[0] : req_addr_if1);
        phys_addr[1] = tlb1_hit[1] ? tlb1_pa[1] : (tlb2_hit[1] ? tlb2_pa[1] : req_addr_if2);
    end

    // Basic ready signals
    assign ready_if1 = req_valid_if1;
    assign ready_if2 = req_valid_if2;

    // Combinational read using translated addresses
    assign data_if1 = data_mem[0][0]; // placeholder
    assign data_if2 = data_mem[0][0]; // placeholder
    assign miss_addr_if1 = req_valid_if1 ? phys_addr[0] : 64'h0;
    assign miss_addr_if2 = req_valid_if2 ? phys_addr[1] : 64'h0;

endmodule
