// amo_unit.sv - Atomic memory operation execution unit
//
// Purpose: Execute basic atomic arithmetic operations for the RV64A
// extension. This placeholder model handles AMOADD.D and AMOSWAP.D in a
// single cycle. Memory access sequencing is expected to be managed by the
// load/store unit.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module amo_unit(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        valid_i,
    input  logic [63:0] op_a_i,
    input  logic [63:0] op_b_i,
    input  logic [4:0]  amo_funct_i, // funct5 field
    output logic        ready_o,
    output logic [63:0] result_o
);

    logic [63:0] result_next;

    always_comb begin
        case (amo_funct_i)
            5'h00: result_next = op_a_i + op_b_i;  // AMOADD
            5'h01: result_next = op_b_i;           // AMOSWAP
            5'h04: result_next = op_a_i ^ op_b_i;  // AMOXOR
            5'h08: result_next = op_a_i | op_b_i;  // AMOOR
            5'h0C: result_next = op_a_i & op_b_i;  // AMOAND
            5'h10: result_next = ($signed(op_a_i) < $signed(op_b_i)) ? op_a_i : op_b_i; // AMOMIN
            5'h14: result_next = ($signed(op_a_i) > $signed(op_b_i)) ? op_a_i : op_b_i; // AMOMAX
            5'h18: result_next = (op_a_i < op_b_i) ? op_a_i : op_b_i; // AMOMINU
            5'h1C: result_next = (op_a_i > op_b_i) ? op_a_i : op_b_i; // AMOMAXU
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
