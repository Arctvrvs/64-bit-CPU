// issue_queue.v
// Placeholder issue queue for out-of-order scheduling.
module issue_queue(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [31:0] instr,
    input  wire [5:0]  phys_src1,
    input  wire [5:0]  phys_src2,
    input  wire [5:0]  phys_dest,
    output wire        ready
);
    assign ready = 1'b1;
endmodule
