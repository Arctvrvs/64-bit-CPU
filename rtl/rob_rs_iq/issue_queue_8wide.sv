// issue_queue_8wide.sv - Simplified issue queue
//
// Purpose: Accepts up to eight micro-ops per cycle and issues ready
// operations in program order. This is a behavioral placeholder model
// with a fixed depth of 128 entries.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module issue_queue_8wide (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        flush_i,

    // Dispatch interface
    input  logic [7:0]  alloc_valid_i,
    input  logic [2:0]  func_type_i [7:0],
    input  logic [63:0] op1_i       [7:0],
    input  logic [63:0] op2_i       [7:0],
    input  logic [63:0] op3_i       [7:0],
    input  logic [63:0] pred_mask_i [7:0],
    input  logic [6:0]  src1_tag_i  [7:0],
    input  logic [6:0]  src2_tag_i  [7:0],
    input  logic [6:0]  src3_tag_i  [7:0],
    input  logic [6:0]  dest_phys_i [7:0],
    input  logic [7:0]  rob_idx_i   [7:0],
    input  logic [7:0]  ready1_i,
    input  logic [7:0]  ready2_i,
    input  logic [7:0]  ready3_i,
    input  logic [6:0]  wakeup_tag_i  [7:0],
    input  logic [63:0] wakeup_data_i [7:0],
    input  logic [7:0]  wakeup_valid_i,
    input  logic [1:0]  fu_int_free_i,
    input  logic        fu_mul_free_i,
    input  logic [1:0]  fu_vec_free_i,
    input  logic [1:0]  fu_mem_free_i,
    input  logic        fu_branch_free_i,
    output logic        iq_full_o,

    // Issue interface (up to eight issues per cycle)
    output logic [7:0]  issue_valid_o,
    output logic [63:0] issue_op1_o     [7:0],
    output logic [63:0] issue_op2_o     [7:0],
    output logic [63:0] issue_op3_o     [7:0],
    output logic [63:0] issue_pred_mask_o [7:0],
    output logic [6:0]  issue_dest_o    [7:0],
    output logic [7:0]  issue_rob_idx_o [7:0]
);

    localparam int Q_SIZE = 128;
    typedef struct packed {
        logic        valid;
        logic [2:0]  func_type;
        logic [63:0] op1;
        logic [63:0] op2;
        logic [63:0] op3;
        logic [63:0] pred_mask;
        logic [6:0]  src1_tag;
        logic [6:0]  src2_tag;
        logic [6:0]  src3_tag;
        logic [6:0]  dest;
        logic [7:0]  rob_idx;
        logic        rdy1;
        logic        rdy2;
        logic        rdy3;
    } iq_entry_t;

    iq_entry_t queue [Q_SIZE-1:0];
    logic [$clog2(Q_SIZE)-1:0] head, tail;
    logic [$clog2(Q_SIZE):0]    count;

    assign iq_full_o = (count >= Q_SIZE-8);

    // Allocate new entries
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || flush_i) begin
            head  <= 0;
            tail  <= 0;
            count <= 0;
            for (int i = 0; i < Q_SIZE; i++) begin
                queue[i].valid <= 1'b0;
            end
        end else begin
            for (int j = 0; j < 8; j++) begin
                if (alloc_valid_i[j] && !iq_full_o) begin
                    queue[tail].valid     <= 1'b1;
                    queue[tail].func_type <= func_type_i[j];
                    queue[tail].op1       <= op1_i[j];
                    queue[tail].op2       <= op2_i[j];
                   queue[tail].op3       <= op3_i[j];
                    queue[tail].pred_mask<= pred_mask_i[j];
                    queue[tail].src1_tag  <= src1_tag_i[j];
                    queue[tail].src2_tag  <= src2_tag_i[j];
                    queue[tail].src3_tag  <= src3_tag_i[j];
                    queue[tail].dest      <= dest_phys_i[j];
                    queue[tail].rob_idx   <= rob_idx_i[j];
                    queue[tail].rdy1      <= ready1_i[j];
                    queue[tail].rdy2      <= ready2_i[j];
                   queue[tail].rdy3      <= ready3_i[j];
                    tail <= tail + 1;
                    count <= count + 1;
                end
            end
        end
    end

    // Wakeup broadcasts
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || flush_i) begin
            // nothing during reset or flush
        end else begin
            for (int w = 0; w < 8; w++) begin
                if (wakeup_valid_i[w]) begin
                    for (int q = 0; q < Q_SIZE; q++) begin
                        if (queue[q].valid) begin
                            if (!queue[q].rdy1 && queue[q].src1_tag == wakeup_tag_i[w]) begin
                                queue[q].op1  <= wakeup_data_i[w];
                                queue[q].rdy1 <= 1'b1;
                            end
                            if (!queue[q].rdy2 && queue[q].src2_tag == wakeup_tag_i[w]) begin
                                queue[q].op2  <= wakeup_data_i[w];
                                queue[q].rdy2 <= 1'b1;
                            end
                            if (!queue[q].rdy3 && queue[q].src3_tag == wakeup_tag_i[w]) begin
                                queue[q].op3  <= wakeup_data_i[w];
                                queue[q].rdy3 <= 1'b1;
                            end
                        end
                    end
                end
            end
        end
    end

    // Issue ready entries (up to eight per cycle)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || flush_i) begin
            for (int k = 0; k < 8; k++) begin
                issue_valid_o[k] <= 1'b0;
                issue_pred_mask_o[k] <= '0;
            end
        end else begin
            logic [1:0] int_avail    = fu_int_free_i;
            logic       mul_avail    = fu_mul_free_i;
            logic [1:0] vec_avail    = fu_vec_free_i;
            logic [1:0] mem_avail    = fu_mem_free_i;
            logic       branch_avail = fu_branch_free_i;

            for (int k = 0; k < 8; k++) begin
                issue_valid_o[k] <= 1'b0;
                issue_pred_mask_o[k] <= '0;
            end

            for (int k = 0; k < 8; k++) begin
                if (queue[head].valid && queue[head].rdy1 && queue[head].rdy2 && queue[head].rdy3) begin
                    case (queue[head].func_type)
                        3'd0: if (int_avail != 0) begin
                            int_avail--;
                            issue_valid_o[k]    <= 1'b1;
                        end
                        3'd1: if (mul_avail != 0) begin
                            mul_avail  <= 1'b0;
                            issue_valid_o[k] <= 1'b1;
                        end
                        3'd2: if (vec_avail != 0) begin
                            vec_avail--;
                            issue_valid_o[k] <= 1'b1;
                        end
                        3'd3: if (mem_avail != 0) begin
                            mem_avail--;
                            issue_valid_o[k] <= 1'b1;
                        end
                        default: if (branch_avail != 0) begin
                            branch_avail <= 1'b0;
                            issue_valid_o[k] <= 1'b1;
                        end
                    endcase

                    if (issue_valid_o[k]) begin
                        issue_op1_o[k]      <= queue[head].op1;
                        issue_op2_o[k]      <= queue[head].op2;
                       issue_op3_o[k]      <= queue[head].op3;
                        issue_pred_mask_o[k]<= queue[head].pred_mask;
                        issue_dest_o[k]     <= queue[head].dest;
                        issue_rob_idx_o[k]  <= queue[head].rob_idx;
                        queue[head].valid   <= 1'b0;
                        head <= head + 1;
                        count <= count - 1;
                    end
                end
            end
        end
    end

endmodule
