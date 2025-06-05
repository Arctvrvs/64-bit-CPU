// vmcs.sv - Virtual Machine Control Structure stub
//
// Purpose: Track the current VM identifier and whether virtualization is
// active. This simple stub allows turning virtualization on/off and
// reading the active VMID.

module vmcs (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       vm_on_i,
    input  logic [7:0] vmid_i,
    input  logic       vm_off_i,
    output logic [7:0] current_vmid_o,
    output logic       running_o
);

    logic [7:0] vmid_r;
    logic       running_r;

    assign current_vmid_o = running_r ? vmid_r : 8'd0;
    assign running_o      = running_r;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            vmid_r   <= 8'd0;
            running_r<= 1'b0;
        end else begin
            if (vm_on_i) begin
                vmid_r   <= vmid_i;
                running_r<= 1'b1;
            end else if (vm_off_i) begin
                running_r<= 1'b0;
            end
        end
    end
endmodule
