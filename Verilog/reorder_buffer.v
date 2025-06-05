// reorder_buffer.v
// Placeholder reorder buffer for committing results in program order.
module reorder_buffer(
    input  wire clk,
    input  wire rst_n,
    input  wire issue_ready,
    output wire commit_ready
);
    assign commit_ready = issue_ready;
endmodule
