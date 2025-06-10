// int_alu2.sv - Dual 64-bit integer ALU pipelines
//
// Purpose: Provides two parallel one-cycle integer ALU pipes used during
// execute stages. Each pipe accepts operands and an ALU operation code and
// returns the result along with destination register bookkeeping.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module int_alu2 (
    input  logic        clk,
    input  logic        rst_n,

    // Pipeline 0 inputs
    input  logic        valid0_i,
    input  logic [63:0] op1_0_i,
    input  logic [63:0] op2_0_i,
    input  logic [3:0]  alu_ctrl_0_i,
    input  logic [6:0]  dest_phys_0_i,
    input  logic [7:0]  rob_idx_0_i,

    // Pipeline 1 inputs
    input  logic        valid1_i,
    input  logic [63:0] op1_1_i,
    input  logic [63:0] op2_1_i,
    input  logic [3:0]  alu_ctrl_1_i,
    input  logic [6:0]  dest_phys_1_i,
    input  logic [7:0]  rob_idx_1_i,

    // Pipeline 0 outputs (valid one cycle later)
    output logic        valid0_o,
    output logic [63:0] result_0_o,
    output logic [6:0]  dest_phys_0_o,
    output logic [7:0]  rob_idx_0_o,

    // Pipeline 1 outputs (valid one cycle later)
    output logic        valid1_o,
    output logic [63:0] result_1_o,
    output logic [6:0]  dest_phys_1_o,
    output logic [7:0]  rob_idx_1_o
);

    // ALU operation codes
    localparam logic [3:0]
        ALU_ADD  = 4'd0,
        ALU_SUB  = 4'd1,
        ALU_AND  = 4'd2,
        ALU_OR   = 4'd3,
        ALU_XOR  = 4'd4,
        ALU_SLL  = 4'd5,
        ALU_SRL  = 4'd6,
        ALU_SRA  = 4'd7;

    // Combinational ALU logic for pipe 0
    logic [63:0] result0;
    always_comb begin
        unique case (alu_ctrl_0_i)
            ALU_ADD: result0 = op1_0_i + op2_0_i;
            ALU_SUB: result0 = op1_0_i - op2_0_i;
            ALU_AND: result0 = op1_0_i & op2_0_i;
            ALU_OR : result0 = op1_0_i | op2_0_i;
            ALU_XOR: result0 = op1_0_i ^ op2_0_i;
            ALU_SLL: result0 = op1_0_i << op2_0_i[5:0];
            ALU_SRL: result0 = op1_0_i >> op2_0_i[5:0];
            ALU_SRA: result0 = $signed(op1_0_i) >>> op2_0_i[5:0];
            default: result0 = 64'd0;
        endcase
    end

    // Combinational ALU logic for pipe 1
    logic [63:0] result1;
    always_comb begin
        unique case (alu_ctrl_1_i)
            ALU_ADD: result1 = op1_1_i + op2_1_i;
            ALU_SUB: result1 = op1_1_i - op2_1_i;
            ALU_AND: result1 = op1_1_i & op2_1_i;
            ALU_OR : result1 = op1_1_i | op2_1_i;
            ALU_XOR: result1 = op1_1_i ^ op2_1_i;
            ALU_SLL: result1 = op1_1_i << op2_1_i[5:0];
            ALU_SRL: result1 = op1_1_i >> op2_1_i[5:0];
            ALU_SRA: result1 = $signed(op1_1_i) >>> op2_1_i[5:0];
            default: result1 = 64'd0;
        endcase
    end

    // Pipeline registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid0_o      <= 1'b0;
            result_0_o    <= 64'd0;
            dest_phys_0_o <= 7'd0;
            rob_idx_0_o   <= 8'd0;
            valid1_o      <= 1'b0;
            result_1_o    <= 64'd0;
            dest_phys_1_o <= 7'd0;
            rob_idx_1_o   <= 8'd0;
        end else begin
            valid0_o      <= valid0_i;
            result_0_o    <= result0;
            dest_phys_0_o <= dest_phys_0_i;
            rob_idx_0_o   <= rob_idx_0_i;

            valid1_o      <= valid1_i;
            result_1_o    <= result1;
            dest_phys_1_o <= dest_phys_1_i;
            rob_idx_1_o   <= rob_idx_1_i;
        end
    end

endmodule
