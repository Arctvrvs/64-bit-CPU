// rsb32.sv - Return stack buffer with 32 entries
//
// Purpose: Stores return addresses for predicting RET instructions.
// Provides push and pop operations with wrap-around behavior.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module rsb32 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        push_i,
    input  logic [63:0] push_addr_i,
    input  logic        pop_i,
    output logic [63:0] top_o,
    output logic        overflow_o,
    output logic        underflow_o
);

    localparam int DEPTH = 32;
    localparam int PTR_W = $clog2(DEPTH);

    logic [63:0] stack[DEPTH-1:0];
    logic [PTR_W-1:0] sp;
    logic [PTR_W:0]   count;

    assign top_o      = (count == 0) ? 64'h0 : stack[sp - 1'b1];
    assign overflow_o = push_i && (count == DEPTH);
    assign underflow_o= pop_i && (count == 0);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sp    <= 0;
            count <= 0;
        end else begin
            if (push_i) begin
                stack[sp] <= push_addr_i;
                if (count < DEPTH) begin
                    count <= count + 1'b1;
                end
                sp <= sp + 1'b1;
            end
            if (pop_i && count != 0) begin
                sp <= sp - 1'b1;
                count <= count - 1'b1;
            end
        end
    end

endmodule
