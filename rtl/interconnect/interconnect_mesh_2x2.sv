// interconnect_mesh_2x2.sv - Simple 2x2 mesh of routers

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module interconnect_mesh_2x2 (
    input logic clk,
    input logic rst_n
);

    router_5port r00 (.*);
    router_5port r01 (.*);
    router_5port r10 (.*);
    router_5port r11 (.*);

endmodule
