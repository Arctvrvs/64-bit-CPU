// debug_unit.v
// Simple debug interface that prints PC and instruction when valid.
module debug_unit(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] pc,
    input  wire [31:0] instr,
    input  wire [63:0] cycle,
    input  wire        valid,
    input  wire        cache_miss,
    input  wire        branch_taken,
    input  wire        stall
);
    always @(posedge clk) begin
        if (rst_n && valid) begin
            $display("DEBUG %0t: PC=%h INSTR=%h miss=%b branch=%b stall=%b", cycle, pc, instr, cache_miss, branch_taken, stall);
        end
    end
endmodule
