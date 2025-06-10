// router_5port.sv - Simple five port mesh router
//
// Purpose: placeholder XY router used to build the on-chip interconnect.
// Each port has a valid/packet input and ready/valid output. This stub
// simply forwards inputs to outputs of the same index when ready.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module router_5port (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [4:0]  in_valid,
    input  logic [4:0][255:0] in_packet,
    input  logic [4:0]  out_ready,
    output logic [4:0]  out_valid,
    output logic [4:0][255:0] out_packet
);

    always_comb begin
        out_valid  = in_valid & out_ready;
        out_packet = in_packet;
    end

endmodule
