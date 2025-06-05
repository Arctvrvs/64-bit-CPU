// branch_predictor_top.sv - Simple branch predictor
//
// Purpose: Provides a very small BTB with 2-bit saturating counters.
// Used by the fetch stage to predict taken branches and their targets.

module branch_predictor_top #(
    parameter int ENTRIES = 32
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [63:0] pc_i,
    output logic        predicted_taken_o,
    output logic [63:0] predicted_target_o,
    // Update interface from execute stage
    input  logic        update_valid_i,
    input  logic [63:0] update_pc_i,
    input  logic        update_taken_i,
    input  logic [63:0] update_target_i
);

    localparam int INDEX_BITS = $clog2(ENTRIES);
    localparam int TAG_BITS   = 64 - INDEX_BITS - 2;

    typedef struct packed {
        logic [TAG_BITS-1:0] tag;
        logic [63:0]         target;
        logic [1:0]          ctr;   // 2-bit saturating counter
    } btb_entry_t;

    btb_entry_t btb[ENTRIES];

    // Predictor lookup
    logic [INDEX_BITS-1:0] lookup_idx;
    assign lookup_idx = pc_i[2 +: INDEX_BITS];

    always_comb begin
        predicted_taken_o  = 1'b0;
        predicted_target_o = pc_i + 64'd4;
        if (btb[lookup_idx].tag == pc_i[2+INDEX_BITS +: TAG_BITS]) begin
            predicted_taken_o  = btb[lookup_idx].ctr[1];
            predicted_target_o = btb[lookup_idx].target;
        end
    end

    // Update on actual branch outcome
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < ENTRIES; i++) begin
                btb[i].tag   <= '0;
                btb[i].target<= '0;
                btb[i].ctr   <= 2'b01; // weakly not taken
            end
        end else if (update_valid_i) begin
            logic [INDEX_BITS-1:0] upd_idx;
            upd_idx = update_pc_i[2 +: INDEX_BITS];
            btb[upd_idx].tag    <= update_pc_i[2+INDEX_BITS +: TAG_BITS];
            btb[upd_idx].target <= update_target_i;
            if (update_taken_i) begin
                if (btb[upd_idx].ctr != 2'b11)
                    btb[upd_idx].ctr <= btb[upd_idx].ctr + 2'b01;
            end else begin
                if (btb[upd_idx].ctr != 2'b00)
                    btb[upd_idx].ctr <= btb[upd_idx].ctr - 2'b01;
            end
        end
    end

endmodule
