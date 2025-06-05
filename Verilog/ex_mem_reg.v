// ex_mem_reg.v
module EX_MEM (
    input  wire        clk,
    input  wire        rst_n,
    // Inputs from EX stage
    input  wire [63:0] ex_pc_plus4,
    input  wire [63:0] ex_alu_result,
    input  wire [63:0] ex_reg_data2,   // for store
    input  wire [4:0]  ex_rd,
    input  wire        ex_zero,        // result == 0 (for BEQ)
    input  wire        ex_reg_write,
    input  wire        ex_mem_read,
    input  wire        ex_mem_write,
    input  wire        ex_mem_to_reg,
    input  wire        ex_branch,
    input  wire [63:0] ex_branch_target,
    // Outputs to MEM stage
    output reg  [63:0] mem_pc_plus4,
    output reg  [63:0] mem_alu_result,
    output reg  [63:0] mem_reg_data2,
    output reg  [4:0]  mem_rd,
    output reg         mem_zero,
    output reg         mem_reg_write,
    output reg         mem_mem_read,
    output reg         mem_mem_write,
    output reg         mem_mem_to_reg,
    output reg         mem_branch,
    output reg  [63:0] mem_branch_target
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mem_pc_plus4     <= 64'b0;
            mem_alu_result   <= 64'b0;
            mem_reg_data2    <= 64'b0;
            mem_rd           <= 5'b0;
            mem_zero         <= 1'b0;
            mem_reg_write    <= 1'b0;
            mem_mem_read     <= 1'b0;
            mem_mem_write    <= 1'b0;
            mem_mem_to_reg   <= 1'b0;
            mem_branch       <= 1'b0;
            mem_branch_target<= 64'b0;
        end else begin
            mem_pc_plus4     <= ex_pc_plus4;
            mem_alu_result   <= ex_alu_result;
            mem_reg_data2    <= ex_reg_data2;
            mem_rd           <= ex_rd;
            mem_zero         <= ex_zero;
            mem_reg_write    <= ex_reg_write;
            mem_mem_read     <= ex_mem_read;
            mem_mem_write    <= ex_mem_write;
            mem_mem_to_reg   <= ex_mem_to_reg;
            mem_branch       <= ex_branch;
            mem_branch_target<= ex_branch_target;
        end
    end
endmodule
