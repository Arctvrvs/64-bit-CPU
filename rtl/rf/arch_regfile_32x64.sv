// arch_regfile_32x64.sv - Architectural Register File
//
// Purpose: Implements the 32 x 64-bit architectural register file used by
// the decode and rename stages. The module provides one synchronous write
// port and three asynchronous read ports.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module arch_regfile_32x64 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        we0,
    input  logic [4:0]  waddr0,
    input  logic [63:0] wdata0,
    input  logic [4:0]  raddr0,
    output logic [63:0] rdata0,
    input  logic [4:0]  raddr1,
    output logic [63:0] rdata1,
    input  logic [4:0]  raddr2,
    output logic [63:0] rdata2
);

    logic [63:0] regfile [31:0];

    // Synchronous write
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < 32; i++) begin
                regfile[i] <= 64'd0;
            end
        end else if (we0) begin
            regfile[waddr0] <= wdata0;
        end
    end

    // Asynchronous reads
    assign rdata0 = regfile[raddr0];
    assign rdata1 = regfile[raddr1];
    assign rdata2 = regfile[raddr2];

endmodule
