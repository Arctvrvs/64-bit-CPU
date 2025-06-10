// pc_fetch.sv - Program counter fetch stage
//
// Purpose: Provide the PC generation logic for the instruction fetch
// pipeline. On each cycle, two sequential instruction addresses are
// produced to drive the L1 instruction cache. Handles branch redirection
// and reset behavior.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module pc_fetch (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        branch_taken_i,
    input  logic [63:0] branch_target_i,
    input  logic [3:0]  flush_id_i, // reserved for future use
    output logic [63:0] pc_if2_o,
    output logic [63:0] pc_if1_plus8_o
);

    parameter logic [63:0] RESET_VECTOR = 64'h0000_0000_8000_0000;

    logic [63:0] pc_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc_reg <= RESET_VECTOR;
        end else if (branch_taken_i) begin
            pc_reg <= branch_target_i;
        end else begin
            pc_reg <= pc_reg + 64'd8;
        end
    end

    assign pc_if2_o       = pc_reg;
    assign pc_if1_plus8_o = pc_reg + 64'd8;

endmodule
