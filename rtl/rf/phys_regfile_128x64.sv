// phys_regfile_128x64.sv - Physical Register File
//
// Purpose: Stores 128 64-bit registers for the out-of-order backend. The module
// provides four synchronous write ports and six asynchronous read ports to
// support up to eight instructions in flight each cycle.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module phys_regfile_128x64 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        we0,
    input  logic [6:0]  waddr0,
    input  logic [63:0] wdata0,
    input  logic        we1,
    input  logic [6:0]  waddr1,
    input  logic [63:0] wdata1,
    input  logic        we2,
    input  logic [6:0]  waddr2,
    input  logic [63:0] wdata2,
    input  logic        we3,
    input  logic [6:0]  waddr3,
    input  logic [63:0] wdata3,
    input  logic [6:0]  raddr0,
    output logic [63:0] rdata0,
    input  logic [6:0]  raddr1,
    output logic [63:0] rdata1,
    input  logic [6:0]  raddr2,
    output logic [63:0] rdata2,
    input  logic [6:0]  raddr3,
    output logic [63:0] rdata3,
    input  logic [6:0]  raddr4,
    output logic [63:0] rdata4,
    input  logic [6:0]  raddr5,
    output logic [63:0] rdata5
);

    logic [63:0] regfile [127:0];

    // Synchronous writes
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < 128; i++) begin
                regfile[i] <= 64'd0;
            end
        end else begin
            if (we0) regfile[waddr0] <= wdata0;
            if (we1) regfile[waddr1] <= wdata1;
            if (we2) regfile[waddr2] <= wdata2;
            if (we3) regfile[waddr3] <= wdata3;
        end
    end

    // Asynchronous reads
    assign rdata0 = regfile[raddr0];
    assign rdata1 = regfile[raddr1];
    assign rdata2 = regfile[raddr2];
    assign rdata3 = regfile[raddr3];
    assign rdata4 = regfile[raddr4];
    assign rdata5 = regfile[raddr5];

endmodule
