// branch_predictor_top.sv - Combined branch predictor
//
// Purpose: Integrates a small BTB, TAGE predictor, indirect branch
// predictor and return stack buffer.  Used by the fetch stage to
// select the next program counter and track branch outcomes.

module branch_predictor_top #(
    parameter int ENTRIES = 32
) (
    input  logic        clk,
    input  logic        rst_n,

    // Decode stage inputs
    input  logic [63:0] pc_id_i,
    input  logic        is_call_i,
    input  logic        is_ret_i,
    input  logic        is_cond_branch_i,
    input  logic        is_uncond_branch_i,
    input  logic        is_indirect_i,
    input  logic [63:0] last_target_i,

    // Prediction outputs
    output logic        pred_taken_o,
    output logic [63:0] predicted_pc_o,

    // Update interface from commit stage
    input  logic        update_valid_i,
    input  logic [63:0] pc_retire_i,
    input  logic        actual_taken_i,
    input  logic [63:0] actual_target_i,
    input  logic        is_branch_retire_i,
    input  logic        is_indirect_retire_i
);

    // Internal predictor wires
    logic        btb_taken;
    logic [63:0] btb_target;
    logic        tage_taken;
    logic [63:0] ibp_target;
    logic [63:0] rsb_top;

    // Instantiate prediction structures
    btb4096_8w btb(
        .clk            (clk),
        .rst_n          (rst_n),
        .req_valid_i    (1'b1),
        .req_pc_i       (pc_id_i),
        .pred_taken_o   (btb_taken),
        .pred_target_o  (btb_target),
        .update_valid_i (update_valid_i && is_branch_retire_i),
        .update_pc_i    (pc_retire_i),
        .update_target_i(actual_target_i),
        .update_taken_i (actual_taken_i)
    );

    tage5 tage(
        .clk            (clk),
        .rst_n          (rst_n),
        .pc_i           (pc_id_i),
        .pred_taken_o   (tage_taken),
        .update_valid_i (update_valid_i && is_branch_retire_i),
        .update_pc_i    (pc_retire_i),
        .update_taken_i (actual_taken_i)
    );

    ibp512_4w ibp(
        .clk            (clk),
        .rst_n          (rst_n),
        .pc_i           (pc_id_i),
        .last_target_i  (last_target_i),
        .pred_target_o  (ibp_target),
        .update_valid_i (update_valid_i && is_indirect_retire_i),
        .update_pc_i    (pc_retire_i),
        .update_target_i(actual_target_i)
    );

    rsb32 rsb(
        .clk        (clk),
        .rst_n      (rst_n),
        .push_i     (is_call_i),
        .push_addr_i(pc_id_i + 64'd4),
        .pop_i      (update_valid_i && is_indirect_retire_i),
        .top_o      (rsb_top)
    );

    // Prediction selection
    always_comb begin
        pred_taken_o     = 1'b0;
        predicted_pc_o   = pc_id_i + 64'd4;

        if (is_ret_i) begin
            pred_taken_o   = 1'b1;
            predicted_pc_o = rsb_top;
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
