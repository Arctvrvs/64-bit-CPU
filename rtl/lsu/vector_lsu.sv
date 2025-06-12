// vector_lsu.sv - Simplified vector load/store unit
//
// Purpose: Issues up to eight lane accesses per cycle. The unit now supports
// simple gather/scatter addressing where each lane address is computed as
// `base + index[i] * scale`. Memory ordering remains ignored.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module vector_lsu (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        valid_i,
    input  logic        is_store_i,
    input  logic [63:0]  base_addr_i,
    input  logic [7:0][63:0] index_i,
    input  logic [2:0]  scale_i,
    input  logic [511:0] store_data_i,
    output logic        req_valid_o,
    output logic [7:0][63:0] req_addr_o,
    output logic [511:0] req_wdata_o,
    output logic        result_valid_o,
    output logic [511:0] load_data_o
);

    always_comb begin
        req_valid_o = valid_i;
        for (int i = 0; i < 8; i++) begin
            req_addr_o[i] = base_addr_i + (index_i[i] << scale_i);
        end
        req_wdata_o = store_data_i;
        result_valid_o = valid_i && !is_store_i;
        load_data_o = 512'd0;
    end

endmodule
