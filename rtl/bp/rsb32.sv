// rsb32.sv - Return stack buffer with 32 entries
//
// Purpose: Stores return addresses for predicting RET instructions.
// Provides push and pop operations with wrap-around behavior.

module rsb32 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        push_i,
    input  logic [63:0] push_addr_i,
    input  logic        pop_i,
    output logic [63:0] top_o
);

    localparam int DEPTH = 32;
    localparam int PTR_W = $clog2(DEPTH);

    logic [63:0] stack[DEPTH-1:0];
    logic [PTR_W-1:0] sp;

    assign top_o = stack[sp - 1'b1];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sp <= 0;
        end else begin
            if (push_i) begin
                stack[sp] <= push_addr_i;
                sp <= sp + 1'b1;
            end
            if (pop_i) begin
                sp <= sp - 1'b1;
            end
        end
    end

endmodule
