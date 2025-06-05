// ept.sv - Extended Page Table stub
//
// Purpose: Translate guest physical addresses to host physical addresses
// using a per-VM XOR key. This is a minimal stand-in for virtualization
// experiments.

module ept #(
    parameter logic [63:0] VM_KEYS[256] = '{default:64'h0}
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        translate_valid_i,
    input  logic [7:0]  vmid_i,
    input  logic [63:0] gpa_i,
    output logic [63:0] hpa_o,
    output logic        fault_o
);

    always_comb begin
        if (translate_valid_i) begin
            hpa_o  = gpa_i ^ VM_KEYS[vmid_i];
            fault_o= 1'b0;
        end else begin
            hpa_o  = 64'd0;
            fault_o= 1'b0;
        end
    end

endmodule
