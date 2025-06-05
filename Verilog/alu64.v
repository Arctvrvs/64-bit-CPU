// alu64.v
module alu64 (
    input  wire [63:0] a,      // operand A
    input  wire [63:0] b,      // operand B
    input  wire [2:0]  alu_op, // operation select
    output reg  [63:0] result, // ALU result
    output wire        zero    // 1 if result == 0
);
    // ALU operation codes
    localparam ALU_ADD  = 3'b000;
    localparam ALU_SUB  = 3'b001;
    localparam ALU_AND  = 3'b010;
    localparam ALU_OR   = 3'b011;
    localparam ALU_XOR  = 3'b100;
    // (You can add more as needed)

    always @(*) begin
        case (alu_op)
            ALU_ADD: result = a + b;
            ALU_SUB: result = a - b;
            ALU_AND: result = a & b;
            ALU_OR:  result = a | b;
            ALU_XOR: result = a ^ b;
            default: result = 64'b0;
        endcase
    end

    assign zero = (result == 64'b0);
endmodule
