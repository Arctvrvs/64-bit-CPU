// tage5.sv - Simplified TAGE predictor with 5 tables
//
// Purpose: Placeholder branch predictor that outputs a taken
// prediction using multiple 2-bit counter tables indexed by PC
// and simple history hashing.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module tage5 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [63:0] pc_i,
    output logic        pred_taken_o,
    input  logic        update_valid_i,
    input  logic [63:0] update_pc_i,
    input  logic        update_taken_i
);
    localparam int TABLES  = 5;
    localparam int ENTRIES = 1024;
    localparam int IDX_BITS = $clog2(ENTRIES);

    typedef struct packed {
        logic [1:0] ctr;
    } entry_t;

    entry_t table[TABLES-1:0][ENTRIES-1:0];
    logic [TABLES-1:0] history;

    function automatic int hash(input logic [63:0] pc, input int t);
        return (pc ^ (history >> t)) & (ENTRIES-1);
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            history <= '0;
            for (int t=0; t<TABLES; t++)
                for (int i=0; i<ENTRIES; i++)
                    table[t][i].ctr <= 2'b01;
        end else if (update_valid_i) begin
            for (int t=0; t<TABLES; t++) begin
                int idx = hash(update_pc_i, t);
                if (update_taken_i) begin
                    if (table[t][idx].ctr != 2'b11)
                        table[t][idx].ctr <= table[t][idx].ctr + 2'b01;
                end else begin
                    if (table[t][idx].ctr != 2'b00)
                        table[t][idx].ctr <= table[t][idx].ctr - 2'b01;
                end
            end
            history <= {history[TABLES-2:0], update_taken_i};
        end
    end

    always_comb begin
        int sum = 0;
        for (int t=0; t<TABLES; t++) begin
            int idx = hash(pc_i, t);
            sum += table[t][idx].ctr[1];
        end
        pred_taken_o = (sum > TABLES/2);
    end
endmodule
