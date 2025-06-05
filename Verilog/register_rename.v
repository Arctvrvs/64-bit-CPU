// register_rename.v
// Minimal register renaming unit.  The free list has been expanded and a
// very small reclaim path allows physical registers to be reused on
// commit.
module register_rename(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] decode_instr,
    output reg         rename_ready,
    output reg [5:0]   phys_src1,
    output reg [5:0]   phys_src2,
    output reg [5:0]   phys_dest,
    input  wire        commit_valid,
    input  wire [5:0]  commit_phys
);
    reg [5:0] free_list[0:31];
    reg [5:0] head, tail;
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head <= 0; tail <= 31;
            rename_ready <= 0;
            for (i = 0; i < 32; i = i + 1) begin
                free_list[i] <= i;
            end
        end else begin
            rename_ready <= 0;
            phys_src1 <= decode_instr[25:21];
            phys_src2 <= decode_instr[20:16];

            if (head != tail) begin
                phys_dest <= free_list[head];
                head <= head + 1;
                rename_ready <= 1;
            end

            // reclaim physical register on commit
            if (commit_valid) begin
                free_list[tail] <= commit_phys;
                tail <= tail + 1;
            end
        end
    end
endmodule
