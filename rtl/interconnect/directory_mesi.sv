// directory_mesi.sv - MESI directory placeholder
module directory_mesi (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_i,
    input  logic [63:0] req_addr_i,
    input  logic        req_write_i,
    input  logic [1:0]  req_src_i,
    output logic        resp_need_inval_o,
    output logic [1:0]  resp_state_o
);
    // No RTL behavior - placeholder for future coherence logic
endmodule
