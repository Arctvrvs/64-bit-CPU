// id_ex_reg.v
module ID_EX (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        stall,          // if we detect a hazard, we want to insert a bubble
    // Inputs from ID stage
    input  wire [63:0] id_pc_plus4,
    input  wire [4:0]  id_rs1,
    input  wire [4:0]  id_rs2,
    input  wire [4:0]  id_rd,
    input  wire [5:0]  id_opcode,
    input  wire [5:0]  id_funct,
    input  wire [15:0] id_imm16,
    input  wire [63:0] id_reg_data1,
    input  wire [63:0] id_reg_data2,
    input  wire        id_reg_write,   // control signals
    input  wire        id_alu_src,
    input  wire [2:0]  id_alu_op,
    input  wire        id_mem_read,
    input  wire        id_mem_write,
    input  wire        id_mem_to_reg,
    input  wire        id_branch,
    // Outputs to EX stage
    output reg  [63:0] ex_pc_plus4,
    output reg  [4:0]  ex_rs1,
    output reg  [4:0]  ex_rs2,
    output reg  [4:0]  ex_rd,
    output reg  [5:0]  ex_opcode,
    output reg  [5:0]  ex_funct,
    output reg  [15:0] ex_imm16,
    output reg  [63:0] ex_reg_data1,
    output reg  [63:0] ex_reg_data2,
    output reg         ex_reg_write,
    output reg         ex_alu_src,
    output reg  [2:0]  ex_alu_op,
    output reg         ex_mem_read,
    output reg         ex_mem_write,
    output reg         ex_mem_to_reg,
    output reg         ex_branch
);
    // On a stall (bubble), we clear all control signals to zero (inserting a NOP)
    wire bubble = stall;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ex_pc_plus4  <= 64'b0;
            ex_rs1       <= 5'b0;
            ex_rs2       <= 5'b0;
            ex_rd        <= 5'b0;
            ex_opcode    <= 6'b0;
            ex_funct     <= 6'b0;
            ex_imm16     <= 16'b0;
            ex_reg_data1 <= 64'b0;
            ex_reg_data2 <= 64'b0;
            ex_reg_write <= 1'b0;
            ex_alu_src   <= 1'b0;
            ex_alu_op    <= 3'b000;
            ex_mem_read  <= 1'b0;
            ex_mem_write <= 1'b0;
            ex_mem_to_reg<= 1'b0;
            ex_branch    <= 1'b0;
        end else if (bubble) begin
            // Insert a NOP by zeroing everything except the PC+4 (we could also zero PC+4, but not strictly necessary)
            ex_pc_plus4  <= id_pc_plus4;
            ex_rs1       <= 5'b0;
            ex_rs2       <= 5'b0;
            ex_rd        <= 5'b0;
            ex_opcode    <= 6'b0;
            ex_funct     <= 6'b0;
            ex_imm16     <= 16'b0;
            ex_reg_data1 <= 64'b0;
            ex_reg_data2 <= 64'b0;
            ex_reg_write <= 1'b0;
            ex_alu_src   <= 1'b0;
            ex_alu_op    <= 3'b000;
            ex_mem_read  <= 1'b0;
            ex_mem_write <= 1'b0;
            ex_mem_to_reg<= 1'b0;
            ex_branch    <= 1'b0;
        end else begin
            ex_pc_plus4  <= id_pc_plus4;
            ex_rs1       <= id_rs1;
            ex_rs2       <= id_rs2;
            ex_rd        <= id_rd;
            ex_opcode    <= id_opcode;
            ex_funct     <= id_funct;
            ex_imm16     <= id_imm16;
            ex_reg_data1 <= id_reg_data1;
            ex_reg_data2 <= id_reg_data2;
            ex_reg_write <= id_reg_write;
            ex_alu_src   <= id_alu_src;
            ex_alu_op    <= id_alu_op;
            ex_mem_read  <= id_mem_read;
            ex_mem_write <= id_mem_write;
            ex_mem_to_reg<= id_mem_to_reg;
            ex_branch    <= id_branch;
        end
    end
endmodule
