// forward_unit.v
module forward_unit (
    input  wire        exmem_reg_write,
    input  wire [4:0]  exmem_rd,
    input  wire        memwb_reg_write,
    input  wire [4:0]  memwb_rd,
    input  wire [4:0]  idex_rs1,
    input  wire [4:0]  idex_rs2,
    output reg  [1:0]  forwardA,  // 00=ID/EX, 10=EX/MEM, 01=MEM/WB
    output reg  [1:0]  forwardB
);
    always @(*) begin
        // Default no forwarding
        forwardA = 2'b00;
        forwardB = 2'b00;

        // Check EX/MEM ? EX forwarding for operand A
        if (exmem_reg_write && (exmem_rd != 5'b0) && (exmem_rd == idex_rs1)) begin
            forwardA = 2'b10;
        end
        // Else check MEM/WB ? EX forwarding for operand A
        else if (memwb_reg_write && (memwb_rd != 5'b0) && (memwb_rd == idex_rs1)) begin
            forwardA = 2'b01;
        end

        // EX/MEM ? EX for operand B
        if (exmem_reg_write && (exmem_rd != 5'b0) && (exmem_rd == idex_rs2)) begin
            forwardB = 2'b10;
        end
        // MEM/WB ? EX for operand B
        else if (memwb_reg_write && (memwb_rd != 5'b0) && (memwb_rd == idex_rs2)) begin
            forwardB = 2'b01;
        end
    end
endmodule
