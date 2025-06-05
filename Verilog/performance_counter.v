// performance_counter.v
// Tracks cycles and instructions for profiling purposes.
module performance_counter(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        instr_valid,
    input  wire        mem_valid,
    input  wire        bp_miss,
    input  wire        branch_taken,
    input  wire        cache_miss,
    input  wire        stall,
    input  wire        flush,
    output reg [63:0]  cycle_count,
    output reg [63:0]  instr_count,
    output reg [63:0]  mem_count,
    output reg [63:0]  bp_miss_count,
    output reg [63:0]  cache_miss_count,
    output reg [63:0]  stall_count,
    output reg [63:0]  flush_count,
    output reg [63:0]  branch_count
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cycle_count      <= 64'b0;
            instr_count      <= 64'b0;
            mem_count        <= 64'b0;
            bp_miss_count    <= 64'b0;
            cache_miss_count <= 64'b0;
            stall_count      <= 64'b0;
            flush_count      <= 64'b0;
            branch_count     <= 64'b0;
        end else begin
            cycle_count <= cycle_count + 64'd1;
            if (instr_valid)
                instr_count <= instr_count + 64'd1;
            if (mem_valid)
                mem_count <= mem_count + 64'd1;
            if (bp_miss)
                bp_miss_count <= bp_miss_count + 64'd1;
            if (cache_miss)
                cache_miss_count <= cache_miss_count + 64'd1;
            if (stall)
                stall_count <= stall_count + 64'd1;
            if (flush)
                flush_count <= flush_count + 64'd1;
            if (branch_taken)
                branch_count <= branch_count + 64'd1;
        end
    end
endmodule
