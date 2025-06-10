// top.sv - Simulation top-level
//
// Purpose: Integrates the four-core SoC and basic memory models. This
// module serves as the entry point for full-chip simulation and future
// FPGA synthesis work. The current implementation simply instantiates
// `riscv_soc_4core` and wires up the clock and reset.
//
// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module top (
    input  logic clk,
    input  logic rst_n
);

    riscv_soc_4core soc (
        .clk  (clk),
        .rst_n(rst_n)
    );

endmodule
