// mem_wb_reg.v
module MEM_WB (
    input  wire        clk,
    input  wire        rst_n,
    // Inputs from MEM stage
    input  wire [63:0] mem_read_data,
    input  wire [63:0] mem_alu_result,
    input  wire [4:0]  mem_rd,
    input  wire        mem_reg_write,
    input  wire        mem_mem_to_reg,
    // Outputs to WB stage
    output reg  [63:0] wb_read_data,
    output reg  [63:0] wb_alu_result,
    output reg  [4:0]  wb_rd,
    output reg         wb_reg_write,
    output reg         wb_mem_to_reg
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wb_read_data   <= 64'b0;
            wb_alu_result  <= 64'b0;
            wb_rd          <= 5'b0;
            wb_reg_write   <= 1'b0;
            wb_mem_to_reg  <= 1'b0;
        end else begin
            wb_read_data   <= mem_read_data;
            wb_alu_result  <= mem_alu_result;
            wb_rd          <= mem_rd;
            wb_reg_write   <= mem_reg_write;
            wb_mem_to_reg  <= mem_mem_to_reg;
        end
    end
endmodule
