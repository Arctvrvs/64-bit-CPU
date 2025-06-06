// l3_cache_16m_8w.sv - Simplified shared L3 cache (16 MB)
//
// For now this model behaves like a large backing memory with a single cycle
// response. Directory and coherence logic are omitted.

module l3_cache_16m_8w (
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

    logic [63:0] mem [0:4095];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            resp_valid_o <= 1'b0;
            resp_rdata_o <= 64'd0;
        end else begin
            if (req_valid_i && resp_ready_i) begin
                resp_valid_o <= 1'b1;
                if (req_write_i) begin
                    mem[req_addr_i[15:3]] <= req_wdata_i;
                    resp_rdata_o <= 64'd0;
                end else begin
                    resp_rdata_o <= mem[req_addr_i[15:3]];
                end
            end else begin
                resp_valid_o <= 1'b0;
            end
        end
    end

endmodule
