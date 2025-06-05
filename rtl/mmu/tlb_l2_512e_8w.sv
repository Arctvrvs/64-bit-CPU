// tlb_l2_512e_8w.sv - 512-entry 8-way level 2 TLB
// Behavioral placeholder providing simple associative lookup

module tlb_l2_512e_8w (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_i,
    input  logic [63:0] req_vaddr_i,
    input  logic [2:0]  req_perm_i,
    output logic        hit_o,
    output logic [63:0] resp_paddr_o,
    output logic        fault_o,

    input  logic        refill_valid_i,
    input  logic [63:0] refill_vaddr_i,
    input  logic [63:0] refill_paddr_i,
    input  logic [2:0]  refill_perm_i
);

    typedef struct packed {
        logic        valid;
        logic [63:0] vaddr;
        logic [63:0] paddr;
        logic [2:0]  perm;
    } tlb_entry_t;

    tlb_entry_t table[512];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < 512; i++) begin
                table[i].valid <= 1'b0;
            end
        end else if (refill_valid_i) begin
            table[refill_vaddr_i[8:0]].valid <= 1'b1;
            table[refill_vaddr_i[8:0]].vaddr <= refill_vaddr_i;
            table[refill_vaddr_i[8:0]].paddr <= refill_paddr_i;
            table[refill_vaddr_i[8:0]].perm  <= refill_perm_i;
        end
    end

    always_comb begin
        tlb_entry_t e = table[req_vaddr_i[8:0]];
        if (req_valid_i && e.valid && e.vaddr == req_vaddr_i) begin
            hit_o        = 1'b1;
            resp_paddr_o = e.paddr;
            fault_o      = (req_perm_i & ~e.perm) != 0;
        end else begin
            hit_o        = 1'b0;
            resp_paddr_o = 64'd0;
            fault_o      = 1'b0;
        end
    end
endmodule
