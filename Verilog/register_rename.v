// register_rename.v
// Placeholder register renaming unit with a simple free list.
module register_rename(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] decode_instr,
    output wire        rename_ready,
    output wire [5:0]  phys_src1,
    output wire [5:0]  phys_src2,
    output wire [5:0]  phys_dest
);
    assign rename_ready = 1'b1;
    assign phys_src1  = decode_instr[25:21];
    assign phys_src2  = decode_instr[20:16];
    assign phys_dest  = decode_instr[15:11];
endmodule
