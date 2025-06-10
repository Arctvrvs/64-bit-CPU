// branch_unit.sv - Branch execution unit
//
// Purpose: Resolve conditional and unconditional branches in a single
// cycle. Computes the actual target and whether the branch is taken,
// comparing the result against the predicted target to detect
// mispredictions.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module branch_unit(
    input  logic        clk,
    input  logic        rst_n,
    input  logic [63:0] pc_ex_i,
    input  logic [63:0] rs1_val_i,
    input  logic [63:0] rs2_val_i,
    input  logic [2:0]  branch_ctrl_i,   // BEQ=0,BNE=1,BLT=2,BGE=3,BLTU=4,BGEU=5,JAL=6,JALR=7
    input  logic [31:0] target_imm_i,    // sign extended immediate
    input  logic        predicted_taken_i,
    input  logic [63:0] predicted_target_i,
    output logic        actual_taken_o,
    output logic [63:0] actual_target_o,
    output logic        pred_mispredict_o
);

    // Combinational branch resolution
    logic [63:0] target;
    logic taken;

    always_comb begin
        target = pc_ex_i + $signed(target_imm_i);
        taken  = 1'b0;
        unique case (branch_ctrl_i)
            3'd0: taken = (rs1_val_i == rs2_val_i);      // BEQ
            3'd1: taken = (rs1_val_i != rs2_val_i);      // BNE
            3'd2: taken = ($signed(rs1_val_i) <  $signed(rs2_val_i)); // BLT
            3'd3: taken = ($signed(rs1_val_i) >= $signed(rs2_val_i)); // BGE
            3'd4: taken = (rs1_val_i < rs2_val_i);       // BLTU
            3'd5: taken = (rs1_val_i >= rs2_val_i);      // BGEU
            3'd6: begin                                  // JAL
                taken  = 1'b1;
                target = pc_ex_i + $signed(target_imm_i);
            end
            3'd7: begin                                  // JALR
                taken  = 1'b1;
                target = (rs1_val_i + $signed(target_imm_i)) & 64'hFFFF_FFFF_FFFF_FFFE;
            end
            default: begin
                taken  = 1'b0;
                target = pc_ex_i + 64'd4;
            end
        endcase
    end

    assign actual_taken_o   = taken;
    assign actual_target_o  = taken ? target : pc_ex_i + 64'd4;
    assign pred_mispredict_o = (predicted_taken_i != actual_taken_o) ||
                               (predicted_taken_i && actual_taken_o && predicted_target_i != actual_target_o);

endmodule
