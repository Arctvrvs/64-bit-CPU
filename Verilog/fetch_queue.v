// fetch_queue.v
// Simple instruction fetch queue placeholder.
module fetch_queue(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] pc_in,
    output wire [63:0] pc_out,
    output wire [31:0] instr_out
);
    // For now just pass through the PC to instruction memory.
    assign pc_out = pc_in;
    assign instr_out = 32'b0;
endmodule
