// fpu_unit.v
// Very small floating point execution unit.  The original version only
// performed a hard coded addition.  It now accepts two operands and an
// opcode so a few basic operations can be demonstrated.
//
// Very small floating point execution unit.  The original version could only
// perform a hard coded addition.  A later revision added basic operations with
// a two stage pipeline.  This update introduces a slightly wider opcode space,
// a third operand for simple fused multiply-add and primitive IEEE exception
// reporting.
//
//  opcode definitions
//  3'd0 - add
//  3'd1 - sub
//  3'd2 - mul
//  3'd3 - div
//  3'd4 - float to int
//  3'd5 - int to float
//  3'd6 - fused multiply-add: src1 * src2 + src3

module fpu_unit(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        issue_valid,
    input  wire [2:0]  opcode,
    input  wire [63:0] src1,
    input  wire [63:0] src2,
    input  wire [63:0] src3,
    output reg         commit_ready,
    output reg [63:0]  result,
    output reg         invalid,
    output reg         overflow,
    output reg         underflow,
    output reg         inexact,
    output reg         div_by_zero
);
    reg valid_s1, valid_s2;
    reg [63:0] op_a_s1, op_b_s1, op_c_s1;
    reg [2:0]  opcode_s1;
    reg [63:0] op_a_s2, op_b_s2, op_c_s2;
    reg [2:0]  opcode_s2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_s1     <= 0;
            valid_s2     <= 0;
            commit_ready <= 0;
            result       <= 0;
            div_by_zero  <= 0;
            invalid      <= 0;
            overflow     <= 0;
            underflow    <= 0;
            inexact      <= 0;
        end else begin
            // stage 1 - latch operands
            valid_s1 <= issue_valid;
            if (issue_valid) begin
                op_a_s1    <= src1;
                op_b_s1    <= src2;
                op_c_s1    <= src3;
                opcode_s1  <= opcode;
            end

            // stage 2 - perform the operation
            valid_s2    <= valid_s1;
            op_a_s2     <= op_a_s1;
            op_b_s2     <= op_b_s1;
            op_c_s2     <= op_c_s1;
            opcode_s2   <= opcode_s1;
            div_by_zero <= 0;
            invalid     <= 0;
            overflow    <= 0;
            underflow   <= 0;
            inexact     <= 0;
            if (valid_s1) begin
                case (opcode_s1)
                    3'd0: result <= $realtobits($bitstoreal(op_a_s1) + $bitstoreal(op_b_s1));
                    3'd1: result <= $realtobits($bitstoreal(op_a_s1) - $bitstoreal(op_b_s1));
                    3'd2: result <= $realtobits($bitstoreal(op_a_s1) * $bitstoreal(op_b_s1));
                    3'd3: begin
                        result <= $realtobits($bitstoreal(op_a_s1) / $bitstoreal(op_b_s1));
                        if (op_b_s1 == 0) div_by_zero <= 1;
                    end
                    3'd4: result <= $signed($bitstoreal(op_a_s1));
                    3'd5: result <= $realtobits($signed(op_a_s1));
                    3'd6: result <= $realtobits(($bitstoreal(op_a_s1) * $bitstoreal(op_b_s1)) + $bitstoreal(op_c_s1));
                endcase
            end

            // stage 3 - result ready
            commit_ready <= valid_s2;
        end
    end
endmodule
