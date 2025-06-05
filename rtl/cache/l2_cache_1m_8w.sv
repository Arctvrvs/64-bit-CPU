// l2_cache_1m_8w.sv - 1 MB 8-way unified L2 cache placeholder
module l2_cache_1m_8w (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_i,
    input  logic [63:0] req_addr_i,
    input  logic        req_write_i,
    input  logic [63:0] req_wdata_i,
    output logic        req_ready_o,
    output logic [63:0] resp_rdata_o
);

    assign req_ready_o = 1'b1;
    assign resp_rdata_o = 64'd0;
endmodule
