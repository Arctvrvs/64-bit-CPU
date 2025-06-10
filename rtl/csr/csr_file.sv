// csr_file.sv - Control and Status Register file
//
// Purpose: Provide a small CSR storage with cycle and instret counters.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module csr_file (
    input  logic        clk,
    input  logic        rst_n,

    input  logic [11:0] raddr_i,
    output logic [63:0] rdata_o,

    input  logic [11:0] waddr_i,
    input  logic [63:0] wdata_i,
    input  logic        we_i,

    input  logic [63:0] instret_inc_i
);

    logic [63:0] csr_mem [0:31];
    logic [63:0] cycle_cnt;
    logic [63:0] instret_cnt;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cycle_cnt   <= 64'd0;
            instret_cnt <= 64'd0;
            for (int i = 0; i < 32; i++) begin
                csr_mem[i] <= 64'd0;
            end
        end else begin
            cycle_cnt   <= cycle_cnt + 1;
            instret_cnt <= instret_cnt + instret_inc_i;
            if (we_i && waddr_i < 32) begin
                csr_mem[waddr_i] <= wdata_i;
            end
        end
    end

    always_comb begin
        case (raddr_i)
            12'hC00: rdata_o = cycle_cnt;
            12'hC02: rdata_o = instret_cnt;
            default: rdata_o = (raddr_i < 32) ? csr_mem[raddr_i] : 64'd0;
        endcase
    end
endmodule
