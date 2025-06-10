// rob256.sv - Reorder Buffer with 256 entries
//
// Purpose: Tracks in-flight micro-operations and commits them in program
// order. Simplified placeholder supporting up to eight allocations and
// eight writebacks per cycle.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module rob256 (
    input  logic        clk,
    input  logic        rst_n,

    // Allocate up to eight new entries per cycle
    input  logic [7:0]  alloc_valid_i,
    input  logic [6:0]  dest_phys_i      [7:0],
    input  logic [6:0]  old_dest_phys_i  [7:0],
    input  logic [7:0]  is_store_i,
    input  logic [7:0]  is_branch_i,
    output logic        alloc_ready_o,
    output logic [7:0]  alloc_idx_o      [7:0],

    // Writeback results
    input  logic [7:0]  wb_valid_i,
    input  logic [7:0]  wb_idx_i      [7:0],
    input  logic [7:0]  wb_branch_misp_i,
    input  logic [63:0] wb_branch_target_i [7:0],

    // Commit interface
    input  logic        commit_ready_i,
    output logic        commit_valid_o,
    output logic [7:0]  commit_idx_o,
    output logic [6:0]  commit_rd_phys_o,
    output logic [6:0]  commit_old_phys_o,
    output logic        commit_is_store_o,
    output logic        commit_branch_misp_o,
    output logic [63:0] commit_branch_target_o
);

    localparam int ROB_ENTRIES = 256;
    typedef struct packed {
        logic        valid;
        logic        ready;
        logic [6:0]  dest_phys;
        logic [6:0]  old_dest_phys;
        logic        is_store;
        logic        is_branch;
        logic        br_misp;
        logic [63:0] br_tgt;
    } rob_entry_t;

    rob_entry_t rob[ROB_ENTRIES-1:0];
    logic [7:0] head_ptr, tail_ptr;
    logic [8:0] count;

    assign alloc_ready_o = (count <= ROB_ENTRIES-8);

    // Allocate new entries
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head_ptr <= 0;
            tail_ptr <= 0;
            count    <= 0;
            for (int i = 0; i < ROB_ENTRIES; i++) begin
                rob[i].valid <= 1'b0;
                rob[i].ready <= 1'b0;
                rob[i].dest_phys <= '0;
                rob[i].old_dest_phys <= '0;
                rob[i].is_store <= 1'b0;
                rob[i].is_branch <= 1'b0;
                rob[i].br_misp <= 1'b0;
                rob[i].br_tgt <= '0;
            end
        end else begin
            if (alloc_ready_o) begin
                for (int j = 0; j < 8; j++) begin
                    if (alloc_valid_i[j]) begin
                        rob[tail_ptr].valid        <= 1'b1;
                        rob[tail_ptr].ready        <= 1'b0;
                        rob[tail_ptr].dest_phys    <= dest_phys_i[j];
                        rob[tail_ptr].old_dest_phys<= old_dest_phys_i[j];
                        rob[tail_ptr].is_store     <= is_store_i[j];
                        rob[tail_ptr].is_branch    <= is_branch_i[j];
                        alloc_idx_o[j]             <= tail_ptr;
                        tail_ptr <= tail_ptr + 1;
                        count    <= count + 1;
                    end else begin
                        alloc_idx_o[j] <= tail_ptr;
                    end
                end
            end

            // Mark entries ready on writeback
            for (int k = 0; k < 8; k++) begin
                if (wb_valid_i[k]) begin
                    rob[wb_idx_i[k]].ready <= 1'b1;
                    rob[wb_idx_i[k]].br_misp <= wb_branch_misp_i[k];
                    rob[wb_idx_i[k]].br_tgt <= wb_branch_target_i[k];
                end
            end

            // Commit oldest entry when ready
            if (commit_ready_i && rob[head_ptr].valid && rob[head_ptr].ready) begin
                commit_valid_o      <= 1'b1;
                commit_idx_o        <= head_ptr;
                commit_rd_phys_o    <= rob[head_ptr].dest_phys;
                commit_old_phys_o   <= rob[head_ptr].old_dest_phys;
                commit_is_store_o   <= rob[head_ptr].is_store;
                commit_branch_misp_o<= rob[head_ptr].br_misp;
                commit_branch_target_o <= rob[head_ptr].br_tgt;
                rob[head_ptr].valid <= 1'b0;
                rob[head_ptr].br_misp <= 1'b0;
                rob[head_ptr].br_tgt <= '0;
                head_ptr <= head_ptr + 1;
                count    <= count - 1;
            end else begin
                commit_valid_o <= 1'b0;
            end
        end
    end

endmodule
