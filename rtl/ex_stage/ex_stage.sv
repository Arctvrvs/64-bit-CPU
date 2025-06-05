// ex_stage.sv - Execution stage wrapper combining functional units
// Handles issued micro-ops from the issue queue and routes them to
// the appropriate functional units. Results are returned on the
// wakeup bus for write back and ROB update.

module ex_stage(
    input logic clk,
    input logic rst_n,
    // Issue interface - up to 8 uops
    input logic [7:0] issue_valid,
    input logic [63:0] op1 [7:0],
    input logic [63:0] op2 [7:0],
    input logic [6:0] dest_phys [7:0],
    input logic [7:0] rob_idx [7:0],
    input logic [3:0] fu_type [7:0], // 0=int,1=mul,2=branch,3=mem,4=vec
    // Wakeup outputs
    output logic [7:0] wb_valid,
    output logic [63:0] wb_data [7:0],
    output logic [6:0] wb_dest [7:0],
    output logic [7:0] wb_rob_idx [7:0]
);

    // For now this is a simple placeholder that immediately forwards
    // operand1 as the result for integer ALU ops and returns after one
    // cycle. Other functional units are modeled with fixed latency.

    typedef struct packed {
        logic valid;
        logic [63:0] data;
        logic [6:0] dest;
        logic [7:0] rob;
        int countdown;
    } fu_entry_t;

    fu_entry_t pending[8];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i=0;i<8;i++) begin
                pending[i].valid <= 0;
                pending[i].countdown <= 0;
            end
        end else begin
            // Advance countdowns
            for (int i=0;i<8;i++) begin
                if (pending[i].valid && pending[i].countdown>0)
                    pending[i].countdown <= pending[i].countdown - 1;
            end
            // Capture new issued ops
            for (int j=0;j<8;j++) begin
                if (issue_valid[j]) begin
                    pending[j].valid <= 1;
                    pending[j].dest <= dest_phys[j];
                    pending[j].rob <= rob_idx[j];
                    case(fu_type[j])
                        0: begin // int ALU
                            pending[j].data <= op1[j] + op2[j]; // simplistic
                            pending[j].countdown <= 1;
                        end
                        default: begin
                            pending[j].data <= 64'h0;
                            pending[j].countdown <= 3;
                        end
                    endcase
                end
            end
            // Produce results
            for (int k=0;k<8;k++) begin
                if (pending[k].valid && pending[k].countdown==0) begin
                    wb_valid[k] <= 1;
                    wb_data[k] <= pending[k].data;
                    wb_dest[k] <= pending[k].dest;
                    wb_rob_idx[k] <= pending[k].rob;
                    pending[k].valid <= 0;
                end else begin
                    wb_valid[k] <= 0;
                end
            end
        end
    end
endmodule
