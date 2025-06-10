// ibp512_4w.sv - Indirect branch predictor
//
// Purpose: Simple associative table that predicts the target of
// indirect branches based on a hash of the PC and last target.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module ibp512_4w (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [63:0] pc_i,
    input  logic [63:0] last_target_i,
    output logic [63:0] pred_target_o,
    input  logic        update_valid_i,
    input  logic [63:0] update_pc_i,
    input  logic [63:0] update_target_i
);
    localparam int ENTRIES = 512;
    localparam int IDX_BITS = $clog2(ENTRIES);

    typedef struct packed {
        logic        valid;
        logic [63:0] tag;
        logic [63:0] target;
    } entry_t;

    entry_t table[ENTRIES-1:0];

    function automatic int hash(input logic [63:0] pc, input logic [63:0] last);
        return (pc ^ last) & (ENTRIES-1);
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i=0; i<ENTRIES; i++) begin
                table[i].valid  <= 1'b0;
                table[i].tag    <= '0;
                table[i].target <= '0;
            end
        end else if (update_valid_i) begin
            int idx = hash(update_pc_i, update_target_i);
            table[idx].valid  <= 1'b1;
            table[idx].tag    <= update_pc_i;
            table[idx].target <= update_target_i;
        end
    end

    always_comb begin
        int idx = hash(pc_i, last_target_i);
        if (table[idx].valid && table[idx].tag == pc_i) begin
            pred_target_o = table[idx].target;
        end else begin
            pred_target_o = 64'd0;
        end
    end
endmodule
