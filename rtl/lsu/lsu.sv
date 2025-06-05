// lsu.sv - Load/Store Unit placeholder
//
// Purpose: Accept up to two memory operations per cycle and interact
// with the L1 data cache. This simplified model completes every
// request in a single cycle using the backing cache.

module lsu (
    input  logic        clk,
    input  logic        rst_n,

    input  logic        op_valid_i[2],
    input  logic        op_is_store_i[2],
    input  logic [63:0] op_addr_i[2],
    input  logic [63:0] op_store_data_i[2],
    input  logic [2:0]  op_store_size_i[2],
    input  logic [6:0]  op_dest_phys_i[2],
    input  logic [7:0]  op_rob_idx_i[2],

    // Interface to L1 D-cache
    output logic        dc_req_valid_o[2],
    output logic [63:0] dc_req_addr_o[2],
    output logic [63:0] dc_req_wdata_o[2],
    output logic [7:0]  dc_req_wstrb_o[2],
    output logic        dc_req_is_write_o[2],
    input  logic        dc_rsp_ready_i[2],
    input  logic [63:0] dc_rsp_rdata_i[2],

    // Results back to ROB
    output logic        result_valid_o[2],
    output logic [63:0] load_data_o[2],
    output logic [6:0]  dest_phys_o[2],
    output logic [7:0]  rob_idx_o[2]
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result_valid_o <= '{default:0};
        end else begin
            for (int i = 0; i < 2; i++) begin
                dc_req_valid_o[i]  <= op_valid_i[i];
                dc_req_addr_o[i]   <= op_addr_i[i];
                dc_req_wdata_o[i]  <= op_store_data_i[i];
                dc_req_is_write_o[i] <= op_is_store_i[i];
                dc_req_wstrb_o[i]  <= op_is_store_i[i] ?
                                        (8'hFF >> (8 - (1 << op_store_size_i[i]))) : 8'h00;
                if (op_valid_i[i] && dc_rsp_ready_i[i]) begin
                    result_valid_o[i] <= !op_is_store_i[i];
                    load_data_o[i]    <= dc_rsp_rdata_i[i];
                    dest_phys_o[i]    <= op_dest_phys_i[i];
                    rob_idx_o[i]      <= op_rob_idx_i[i];
                end else begin
                    result_valid_o[i] <= 1'b0;
                end
            end
        end
    end

endmodule
