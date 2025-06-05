// branch_predictor.v
// Simple 2-bit saturating counter branch predictor
module branch_predictor (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] pc_fetch,     // PC of branch to predict
    input  wire        update_valid, // update with actual outcome
    input  wire        update_taken,
    input  wire [63:0] update_pc,    // PC of branch being updated
    output wire        predict_taken
);
    localparam BHT_ENTRIES = 64;
    reg [1:0] bht [0:BHT_ENTRIES-1];
    integer i;

    wire [5:0] fetch_idx  = pc_fetch[7:2];
    wire [5:0] update_idx = update_pc[7:2];

    // Predict taken if MSB of counter is 1
    assign predict_taken = bht[fetch_idx][1];

    // Initialize BHT to weakly not taken
    initial begin
        for (i = 0; i < BHT_ENTRIES; i = i + 1) begin
            bht[i] = 2'b01; // weak not taken
        end
    end

    // Update BHT on branch resolution
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < BHT_ENTRIES; i = i + 1) begin
                bht[i] <= 2'b01;
            end
        end else if (update_valid) begin
            if (update_taken) begin
                if (bht[update_idx] != 2'b11)
                    bht[update_idx] <= bht[update_idx] + 2'b01;
            end else begin
                if (bht[update_idx] != 2'b00)
                    bht[update_idx] <= bht[update_idx] - 2'b01;
            end
        end
    end
endmodule
