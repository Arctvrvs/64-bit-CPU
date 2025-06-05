// issue_queue_8wide.sv - Simplified issue queue
//
// Purpose: Accepts up to eight micro-ops per cycle and issues ready
// operations in program order. This is a behavioral placeholder model
// with a small fixed depth.

module issue_queue_8wide (
    input  logic        clk,
    input  logic        rst_n,

    // Dispatch interface
    input  logic [7:0]  alloc_valid_i,
    input  logic [63:0] op1_i       [7:0],
    input  logic [63:0] op2_i       [7:0],
    input  logic [6:0]  dest_phys_i [7:0],
    input  logic [7:0]  rob_idx_i   [7:0],
    input  logic [7:0]  ready1_i,
    input  logic [7:0]  ready2_i,
    output logic        iq_full_o,

    // Issue interface (up to two issued per cycle for this model)
    output logic [1:0]  issue_valid_o,
    output logic [63:0] issue_op1_o     [1:0],
    output logic [63:0] issue_op2_o     [1:0],
    output logic [6:0]  issue_dest_o    [1:0],
    output logic [7:0]  issue_rob_idx_o [1:0]
);

    localparam int Q_SIZE = 16;
    typedef struct packed {
        logic        valid;
        logic [63:0] op1;
        logic [63:0] op2;
        logic [6:0]  dest;
        logic [7:0]  rob_idx;
        logic        rdy1;
        logic        rdy2;
    } iq_entry_t;

    iq_entry_t queue [Q_SIZE-1:0];
    logic [$clog2(Q_SIZE)-1:0] head, tail;
    logic [4:0] count;

    assign iq_full_o = (count >= Q_SIZE-8);

    // Allocate new entries
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head  <= 0;
            tail  <= 0;
            count <= 0;
            for (int i = 0; i < Q_SIZE; i++) begin
                queue[i].valid <= 1'b0;
            end
        end else begin
            for (int j = 0; j < 8; j++) begin
                if (alloc_valid_i[j] && !iq_full_o) begin
                    queue[tail].valid   <= 1'b1;
                    queue[tail].op1     <= op1_i[j];
                    queue[tail].op2     <= op2_i[j];
                    queue[tail].dest    <= dest_phys_i[j];
                    queue[tail].rob_idx <= rob_idx_i[j];
                    queue[tail].rdy1    <= ready1_i[j];
                    queue[tail].rdy2    <= ready2_i[j];
                    tail <= tail + 1;
                    count <= count + 1;
                end
            end
        end
    end

    // Issue ready entries (up to two per cycle)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            issue_valid_o[0] <= 1'b0;
            issue_valid_o[1] <= 1'b0;
        end else begin
            issue_valid_o[0] <= 1'b0;
            issue_valid_o[1] <= 1'b0;
            for (int k = 0; k < 2; k++) begin
                if (queue[head].valid && queue[head].rdy1 && queue[head].rdy2) begin
                    issue_valid_o[k]    <= 1'b1;
                    issue_op1_o[k]      <= queue[head].op1;
                    issue_op2_o[k]      <= queue[head].op2;
                    issue_dest_o[k]     <= queue[head].dest;
                    issue_rob_idx_o[k]  <= queue[head].rob_idx;
                    queue[head].valid   <= 1'b0;
                    head <= head + 1;
                    count <= count - 1;
                end
            end
        end
    end

endmodule
