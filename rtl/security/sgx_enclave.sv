// sgx_enclave.sv - Minimal SGX enclave controller stub
//
// Purpose: Provide a toy model for enclave creation and entry/exit logic.
// It keeps a bitmap of allocated enclave pages and raises a fault when
// accessing memory outside the enclave while active.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module sgx_enclave (
    input  logic        clk,
    input  logic        rst_n,

    input  logic        ecreate_i,
    input  logic        eadd_i,
    input  logic        einit_i,
    input  logic        eenter_i,
    input  logic        eexit_i,
    input  logic [63:0] addr_i,
    input  logic [63:0] wdata_i,
    input  logic [63:0] access_addr_i,

    output logic        active_o,
    output logic        sgx_fault_o
);

    localparam int PAGES = 256;
    logic [PAGES-1:0] epcm;
    logic        active_r;
    logic [63:0] epc_mem [PAGES-1:0];

    assign active_o = active_r;

    // page index derived from address bits [15:8]
    function automatic int page_idx(input logic [63:0] a);
        return int'(a[15:8]);
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            epcm      <= '0;
            active_r  <= 1'b0;
        end else begin
            if (ecreate_i) begin
                epcm[page_idx(addr_i)] <= 1'b1;
            end
            if (eadd_i) begin
                epcm[page_idx(addr_i)] <= 1'b1;
                epc_mem[page_idx(addr_i)] <= wdata_i;
            end
            if (einit_i) begin
                // measurement ignored in stub
            end
            if (eenter_i) begin
                active_r <= 1'b1;
            end
            if (eexit_i) begin
                active_r <= 1'b0;
            end
        end
    end

    always_comb begin
        if (active_r && !epcm[page_idx(access_addr_i)])
            sgx_fault_o = 1'b1;
        else
            sgx_fault_o = 1'b0;
    end

endmodule
