// branch_predictor_top.sv - Composite branch predictor
//
// Purpose: Integrates return stack buffer, BTB, TAGE and indirect
// branch predictor. Provides a simple interface for the fetch stage
// and update signals from the commit stage.

module branch_predictor_top (
    input  logic        clk,
    input  logic        rst_n,
    // ID stage inputs
    input  logic [63:0] pc_id_i,
    input  logic        is_call_i,
    input  logic        is_ret_i,
    input  logic        is_cond_branch_i,
    input  logic        is_uncond_branch_i,
    input  logic        is_indirect_i,
    input  logic [63:0] last_target_i,
    // Commit stage update
    input  logic        update_valid_i,
    input  logic [63:0] pc_retire_i,
    input  logic        actual_taken_i,
    input  logic [63:0] actual_target_i,
    input  logic        is_branch_retire_i,
    input  logic        is_indirect_retire_i,
    output logic [63:0] predicted_pc_o,
    output logic        pred_taken_o
);
    // Instantiate structures
    rsb32 rsb(
        .clk(clk),
        .rst_n(rst_n),
        .push_i(is_call_i),
        .push_addr_i(pc_id_i + 64'd4),
        .pop_i(is_ret_i),
        .top_o()
    );
    logic [63:0] rsb_target;
    assign rsb_target = rsb.top_o;

    btb4096_8w btb(
        .clk(clk),
        .rst_n(rst_n),
        .req_valid_i(is_cond_branch_i | is_uncond_branch_i),
        .req_pc_i(pc_id_i),
        .pred_taken_o(),
        .pred_target_o(),
        .update_valid_i(update_valid_i && is_branch_retire_i),
        .update_pc_i(pc_retire_i),
        .update_target_i(actual_target_i),
        .update_taken_i(actual_taken_i)
    );
    logic btb_taken;
    logic [63:0] btb_target;
    assign btb_taken  = btb.pred_taken_o;
    assign btb_target = btb.pred_target_o;

    tage5 tage(
        .clk(clk),
        .rst_n(rst_n),
        .pc_i(pc_id_i),
        .pred_taken_o(),
        .update_valid_i(update_valid_i && is_branch_retire_i),
        .update_pc_i(pc_retire_i),
        .update_taken_i(actual_taken_i)
    );
    logic tage_taken;
    assign tage_taken = tage.pred_taken_o;

    ibp512_4w ibp(
        .clk(clk),
        .rst_n(rst_n),
        .pc_i(pc_id_i),
        .last_target_i(last_target_i),
        .pred_target_o(),
        .update_valid_i(update_valid_i && is_indirect_retire_i),
        .update_pc_i(pc_retire_i),
        .update_target_i(actual_target_i)
    );
    logic [63:0] ibp_target;
    assign ibp_target = ibp.pred_target_o;

    always_comb begin
        pred_taken_o    = 1'b0;
        predicted_pc_o  = pc_id_i + 64'd4;
        if (is_ret_i) begin
            pred_taken_o   = 1'b1;
            predicted_pc_o = rsb_target;
        end else if (is_uncond_branch_i) begin
            pred_taken_o   = 1'b1;
            predicted_pc_o = btb_target;
        end else if (is_cond_branch_i) begin
            pred_taken_o   = tage_taken;
            predicted_pc_o = tage_taken ? btb_target : (pc_id_i + 64'd4);
        end else if (is_indirect_i) begin
            pred_taken_o   = 1'b1;
            predicted_pc_o = ibp_target;
        end
    end
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
