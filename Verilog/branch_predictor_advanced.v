// branch_predictor_advanced.v
// Simple 2-bit counter predictor with a tiny branch target buffer.  This
// provides a slightly more realistic placeholder than the previous static
// predictor.
module branch_predictor_advanced(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] pc_fetch,
    output wire        predict_taken,
    output wire [63:0] predict_target,
    input  wire        update_valid,
    input  wire [63:0] update_pc,
    input  wire        update_taken,
    input  wire [63:0] update_target
);
    localparam BHT_ENTRIES = 64;
    localparam BTB_ENTRIES = 16;

    // 2-bit saturating counters for taken/not taken history
    reg [1:0] bht [0:BHT_ENTRIES-1];

    // Very small branch target buffer indexed by bits [5:2] of the PC
    reg [63:0] btb_pc     [0:BTB_ENTRIES-1];
    reg [63:0] btb_target [0:BTB_ENTRIES-1];

    integer i;

    wire [5:0] bht_idx = pc_fetch[7:2];
    wire [3:0] btb_idx = pc_fetch[5:2];

    // Lookup BTB entry
    reg        btb_hit;
    reg [63:0] btb_target_r;
    always @(*) begin
        if (btb_pc[btb_idx] == pc_fetch) begin
            btb_hit      = 1'b1;
            btb_target_r = btb_target[btb_idx];
        end else begin
            btb_hit      = 1'b0;
            btb_target_r = pc_fetch + 64'd4;
        end
    end

    assign predict_taken  = bht[bht_idx][1];
    assign predict_target = btb_target_r;

    // Initialize predictor state
    initial begin
        for (i = 0; i < BHT_ENTRIES; i = i + 1) begin
            bht[i] = 2'b01; // weak not taken
        end
        for (i = 0; i < BTB_ENTRIES; i = i + 1) begin
            btb_pc[i]     = 64'b0;
            btb_target[i] = 64'b0;
        end
    end

    wire [5:0] bht_update_idx = update_pc[7:2];
    wire [3:0] btb_update_idx = update_pc[5:2];

    // Update structures on branch resolution
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < BHT_ENTRIES; i = i + 1) begin
                bht[i] <= 2'b01;
            end
            for (i = 0; i < BTB_ENTRIES; i = i + 1) begin
                btb_pc[i]     <= 64'b0;
                btb_target[i] <= 64'b0;
            end
        end else if (update_valid) begin
            // Update counter
            if (update_taken) begin
                if (bht[bht_update_idx] != 2'b11)
                    bht[bht_update_idx] <= bht[bht_update_idx] + 2'b01;
            end else begin
                if (bht[bht_update_idx] != 2'b00)
                    bht[bht_update_idx] <= bht[bht_update_idx] - 2'b01;
            end

            // Update BTB for taken branches
            if (update_taken) begin
                btb_pc[btb_update_idx]     <= update_pc;
                btb_target[btb_update_idx] <= update_target;
            end
        end
    end
endmodule
