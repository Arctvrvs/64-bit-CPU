// smt_arbitration.sv - simple round-robin SMT scheduler for two threads

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module smt_arbitration(
    input logic clk,
    input logic rst_n,
    input logic t0_req,
    input logic t1_req,
    output logic grant_t0,
    output logic grant_t1
);
    logic last;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            last <= 0;
        end else begin
            if (t0_req && t1_req) begin
                last <= ~last;
            end else if (t0_req || t1_req) begin
                last <= t1_req;
            end
        end
    end

    assign grant_t0 = t0_req && (!t1_req || !last);
    assign grant_t1 = t1_req && (!t0_req || last);
endmodule
