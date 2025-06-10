// btb4096_8w.sv - 4096 entry 8-way Branch Target Buffer
//
// Purpose: Predict branch targets for the fetch stage. This is a behavioral
// placeholder with simple associative lookup and update logic.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module btb4096_8w (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        req_valid_i,
    input  logic [63:0] req_pc_i,
    output logic        pred_taken_o,
    output logic [63:0] pred_target_o,

    input  logic        update_valid_i,
    input  logic [63:0] update_pc_i,
    input  logic [63:0] update_target_i,
    input  logic        update_taken_i
);

    // Simplified direct mapped BTB for early development
    localparam int SETS = 4096;
    typedef struct packed {
        logic        valid;
        logic [51:0] tag;  // 64-12
        logic [63:0] target;
    } btb_entry_t;

    btb_entry_t table[SETS];

    logic [11:0] index;
    logic [51:0] tag;

    assign index = req_pc_i[13:2];
    assign tag   = req_pc_i[63:12];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < SETS; i++) begin
                table[i].valid  <= 1'b0;
                table[i].tag    <= 0;
                table[i].target <= 0;
            end
        end else begin
            if (update_valid_i) begin
                table[update_pc_i[13:2]].valid  <= update_taken_i;
                table[update_pc_i[13:2]].tag    <= update_pc_i[63:12];
                table[update_pc_i[13:2]].target <= update_target_i;
            end
        end
    end

    always_comb begin
        if (table[index].valid && table[index].tag == tag) begin
            pred_taken_o  = 1'b1;
            pred_target_o = table[index].target;
        end else begin
            pred_taken_o  = 1'b0;
            pred_target_o = req_pc_i + 64'd4;
        end
    end

endmodule
