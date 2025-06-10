// dram_model.sv - Tiny behavioral DRAM

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module dram_model (
    input  logic        clk,
    input  logic        req_valid,
    input  logic        req_write,
    input  logic [63:0] req_addr,
    input  logic [63:0] req_wdata,
    input  logic        resp_ready,
    output logic        resp_valid,
    output logic [63:0] resp_rdata
);

    logic [63:0] mem [0:2047];

    always_ff @(posedge clk) begin
        if (req_valid && resp_ready) begin
            resp_valid <= 1'b1;
            if (req_write)
                mem[req_addr[14:3]] <= req_wdata;
            resp_rdata <= mem[req_addr[14:3]];
        end else begin
            resp_valid <= 1'b0;
        end
    end

endmodule
