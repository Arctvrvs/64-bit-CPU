// tlb_l1_64e_8w.sv - Instruction/Data L1 TLB placeholder
//
// Purpose: Translates virtual addresses to physical addresses using a
// small fully associative table. This simplified model assumes
// single-cycle lookup and direct refill interface.

(* clock_gating_cell = "yes" *)
module tlb_l1_64e_8w #(
    parameter int ENTRIES = 64
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        lookup_valid,
    input  logic [63:0] va_i,
    input  logic [2:0]  perm_req_i, // bit0=read, bit1=write, bit2=exec
    output logic        hit_o,
    output logic [63:0] pa_o,
    output logic        perm_fault_o,
    input  logic        refill_valid,
    input  logic [63:0] refill_va_i,
    input  logic [63:0] refill_pa_i,
    input  logic [2:0]  refill_perm_i
);
    // Simplified associative array
    typedef struct packed {
        logic        valid;
        logic [51:12] tag; // VPN
        logic [51:12] ppn;
        logic [2:0]   perm;
    } entry_t;

    entry_t table [ENTRIES-1:0];

    integer i;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < ENTRIES; i++) begin
                table[i].valid <= 1'b0;
            end
        end else begin
            if (refill_valid) begin
                table[0] <= '{valid:1'b1, tag:refill_va_i[63:12],
                             ppn:refill_pa_i[63:12], perm:refill_perm_i};
            end
        end
    end

    // Combinational lookup
    always_comb begin
        hit_o        = 1'b0;
        pa_o         = 64'h0;
        perm_fault_o = 1'b0;
        for (i = 0; i < ENTRIES; i++) begin
            if (table[i].valid && table[i].tag == va_i[63:12]) begin
                hit_o = 1'b1;
                pa_o  = {table[i].ppn, va_i[11:0]};
                perm_fault_o = |(perm_req_i & ~table[i].perm);
            end
        end
    end
endmodule
