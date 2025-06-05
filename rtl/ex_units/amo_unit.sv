// amo_unit.sv - Atomic memory operation execution unit
//
// Purpose: Execute basic atomic arithmetic operations for the RV64A
// extension. This placeholder model handles AMOADD.D and AMOSWAP.D in a
// single cycle. Memory access sequencing is expected to be managed by the
// load/store unit.

module amo_unit(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        valid_i,
    input  logic [63:0] op_a_i,
    input  logic [63:0] op_b_i,
    input  logic [2:0]  amo_funct_i, // 0=add,1=swap
    output logic        ready_o,
    output logic [63:0] result_o
);

    logic [63:0] result_next;

    always_comb begin
        case (amo_funct_i)
            3'd0: result_next = op_a_i + op_b_i;  // AMOADD
            3'd1: result_next = op_b_i;           // AMOSWAP
            default: result_next = op_a_i;
        endcase
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result_o <= 64'd0;
            ready_o  <= 1'b0;
        end else begin
            if (valid_i) begin
                result_o <= result_next;
                ready_o  <= 1'b1;
            end else begin
                ready_o  <= 1'b0;
            end
        end
    end

endmodule
