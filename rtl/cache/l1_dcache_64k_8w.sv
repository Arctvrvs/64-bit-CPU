// l1_dcache_64k_8w.sv - 64 KB 8-way set associative data cache (placeholder)
//
// Purpose: Provides a simple behavioral L1 D-cache model with two
// read/write ports. Each access completes in one cycle and is backed
// by an internal memory array. This module is a minimal stand-in for
// development and does not implement tags, replacement or miss logic.

module l1_dcache_64k_8w #(
    parameter int LINE_BYTES = 64,
    parameter int ASSOC      = 8,
    parameter int SETS       = 128
) (
    input  logic        clk,
    input  logic        rst_n,

    input  logic        req_valid_i[2],
    input  logic [63:0] req_addr_i[2],
    input  logic [63:0] req_wdata_i[2],
    input  logic [7:0]  req_wstrb_i[2],
    input  logic        req_is_write_i[2],

    output logic        rsp_ready_o[2],
    output logic [63:0] rsp_rdata_o[2]
);

    // Simple backing memory (64 KB)
    logic [63:0] mem [0:8191];

    // Requests complete in one cycle
    always_ff @(posedge clk) begin
        for (int i = 0; i < 2; i++) begin
            if (req_valid_i[i]) begin
                if (req_is_write_i[i]) begin
                    for (int b = 0; b < 8; b++) begin
                        if (req_wstrb_i[i][b])
                            mem[req_addr_i[i][15:3]][8*b +: 8] <= req_wdata_i[i][8*b +: 8];
                    end
                end else begin
                    rsp_rdata_o[i] <= mem[req_addr_i[i][15:3]];
                end
            end
        end
    end

    assign rsp_ready_o[0] = req_valid_i[0];
    assign rsp_ready_o[1] = req_valid_i[1];

endmodule
