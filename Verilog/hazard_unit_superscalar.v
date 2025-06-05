// hazard_unit_superscalar.v
// Basic cross-lane hazard detection for dual issue
module hazard_unit_superscalar(
    input  wire       lane0_mem_read,
    input  wire [4:0] lane0_rd,
    input  wire [4:0] lane1_rs1,
    input  wire [4:0] lane1_rs2,
    output reg        stall_lane1
);
    always @(*) begin
        if (lane0_mem_read && ((lane0_rd == lane1_rs1) || (lane0_rd == lane1_rs2))) begin
            stall_lane1 = 1'b1;
        end else begin
            stall_lane1 = 1'b0;
        end
    end
endmodule
