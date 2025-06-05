// muldiv_unit.sv - 64-bit multiply/divide execution unit
//
// Purpose: Provides a 3-stage pipelined multiplier and a 20-stage
// divider used by the execution stages. Operations are issued
// independently for multiply and divide. Results are returned with
// associated destination register and ROB index after the
// appropriate latency.

module muldiv_unit #(
    parameter int MUL_STAGES = 3,
    parameter int DIV_STAGES = 20
) (
    input  logic        clk,
    input  logic        rst_n,

    // Multiply input
    input  logic        mul_valid_i,
    input  logic [63:0] mul_op_a_i,
    input  logic [63:0] mul_op_b_i,
    input  logic [6:0]  mul_dest_phys_i,
    input  logic [7:0]  mul_rob_idx_i,

    // Divide input
    input  logic        div_valid_i,
    input  logic [63:0] div_dividend_i,
    input  logic [63:0] div_divisor_i,
    input  logic [6:0]  div_dest_phys_i,
    input  logic [7:0]  div_rob_idx_i,

    // Multiply output (valid after 3 cycles)
    output logic        mul_valid_o,
    output logic [63:0] mul_result_o,
    output logic [6:0]  mul_dest_phys_o,
    output logic [7:0]  mul_rob_idx_o,

    // Divide output (valid after 20 cycles)
    output logic        div_valid_o,
    output logic [63:0] div_result_o,
    output logic [6:0]  div_dest_phys_o,
    output logic [7:0]  div_rob_idx_o
);

    // Multiply pipeline registers
    logic [MUL_STAGES-1:0]        mul_valid_pipe;
    logic [63:0]                  mul_result_pipe [MUL_STAGES-1:0];
    logic [6:0]                   mul_dest_pipe   [MUL_STAGES-1:0];
    logic [7:0]                   mul_rob_pipe    [MUL_STAGES-1:0];

    // Divide pipeline registers
    logic [DIV_STAGES-1:0]        div_valid_pipe;
    logic [63:0]                  div_result_pipe [DIV_STAGES-1:0];
    logic [6:0]                   div_dest_pipe   [DIV_STAGES-1:0];
    logic [7:0]                   div_rob_pipe    [DIV_STAGES-1:0];

    // Shift pipelines
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mul_valid_pipe <= '0;
            div_valid_pipe <= '0;
        end else begin
            // Multiply pipeline stage 0 computation
            mul_valid_pipe[0]  <= mul_valid_i;
            mul_result_pipe[0] <= mul_op_a_i * mul_op_b_i;
            mul_dest_pipe[0]   <= mul_dest_phys_i;
            mul_rob_pipe[0]    <= mul_rob_idx_i;

            // Divide pipeline stage 0 computation
            div_valid_pipe[0]  <= div_valid_i;
            div_result_pipe[0] <= (div_divisor_i == 0) ? 64'd0 : div_dividend_i / div_divisor_i;
            div_dest_pipe[0]   <= div_dest_phys_i;
            div_rob_pipe[0]    <= div_rob_idx_i;

            // Shift remaining multiply pipeline stages
            for (int i = 1; i < MUL_STAGES; i++) begin
                mul_valid_pipe[i]  <= mul_valid_pipe[i-1];
                mul_result_pipe[i] <= mul_result_pipe[i-1];
                mul_dest_pipe[i]   <= mul_dest_pipe[i-1];
                mul_rob_pipe[i]    <= mul_rob_pipe[i-1];
            end

            // Shift remaining divide pipeline stages
            for (int j = 1; j < DIV_STAGES; j++) begin
                div_valid_pipe[j]  <= div_valid_pipe[j-1];
                div_result_pipe[j] <= div_result_pipe[j-1];
                div_dest_pipe[j]   <= div_dest_pipe[j-1];
                div_rob_pipe[j]    <= div_rob_pipe[j-1];
            end
        end
    end

    assign mul_valid_o      = mul_valid_pipe[MUL_STAGES-1];
    assign mul_result_o     = mul_result_pipe[MUL_STAGES-1];
    assign mul_dest_phys_o  = mul_dest_pipe[MUL_STAGES-1];
    assign mul_rob_idx_o    = mul_rob_pipe[MUL_STAGES-1];

    assign div_valid_o      = div_valid_pipe[DIV_STAGES-1];
    assign div_result_o     = div_result_pipe[DIV_STAGES-1];
    assign div_dest_phys_o  = div_dest_pipe[DIV_STAGES-1];
    assign div_rob_idx_o    = div_rob_pipe[DIV_STAGES-1];

endmodule
