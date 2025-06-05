// l3_slice_4m_8w.sv - Placeholder L3 cache slice
//
// Holds a small associative array to service requests from L2 caches.

module l3_slice_4m_8w (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_i,
    input  logic [63:0] req_addr_i,
    input  logic        req_write_i,
    input  logic [63:0] req_wdata_i,
    input  logic        resp_ready_i,
    output logic        resp_valid_o,
    output logic [63:0] resp_rdata_o
);

    // simple memory model
    logic [63:0] mem [0:1023];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            resp_valid_o <= 1'b0;
            resp_rdata_o <= 64'd0;
        end else begin
            if (req_valid_i && resp_ready_i) begin
                resp_valid_o <= 1'b1;
                if (req_write_i) begin
                    mem[req_addr_i[13:3]] <= req_wdata_i;
                    resp_rdata_o <= 64'd0;
                end else begin
                    resp_rdata_o <= mem[req_addr_i[13:3]];
                end
            end else begin
                resp_valid_o <= 1'b0;
            end
        end
    end

endmodule
