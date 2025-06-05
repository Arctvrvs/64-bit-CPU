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
endmodule
