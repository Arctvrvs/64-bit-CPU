// page_walker8.sv - Simplified page table walker supporting up to 8 concurrent requests
//
// Each request is translated using an internal associative array. This model
// returns a result in a single cycle and does not perform real page table walks.

module page_walker8 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic  [7:0] walk_valid_i,
    input  logic [63:0] walk_vaddr_i [8],
    input  logic  [2:0] walk_perm_i  [8],
    output logic  [7:0] walk_ready_o,
    output logic  [7:0] resp_valid_o,
    output logic [63:0] resp_paddr_o [8],
    output logic  [7:0] resp_fault_o
);

    typedef struct packed {
        logic        valid;
        logic [63:0] vaddr;
        logic [63:0] paddr;
        logic [2:0]  perm;
    } entry_t;

    entry_t table [16];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < 16; i++) table[i].valid <= 1'b0;
        end
    end

    // Simple lookup per request
    always_comb begin
        for (int k = 0; k < 8; k++) begin
            resp_valid_o[k] = 1'b0;
            resp_paddr_o[k] = 64'd0;
            resp_fault_o[k] = 1'b0;
            walk_ready_o[k] = 1'b1;
            for (int i = 0; i < 16; i++) begin
                if (table[i].valid && table[i].vaddr == walk_vaddr_i[k]) begin
                    resp_valid_o[k] = walk_valid_i[k];
                    resp_paddr_o[k] = table[i].paddr;
                    resp_fault_o[k] = |(walk_perm_i[k] & ~table[i].perm);
                end
            end
        end
    end
endmodule
