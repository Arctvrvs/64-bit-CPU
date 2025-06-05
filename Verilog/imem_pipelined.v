// imem_pipelined.v
module imem_pipelined (
    input  wire [63:0] addr,    // PC byte address
    output reg  [31:0] instr
);
    reg [31:0] rom [0:255];

    // Declare loop index at module scope, not inside initial
    integer i;

    initial begin
        // Instead of manually writing, you can generate a .hex file from an assembler
        // and do: $readmemh("program.hex", rom);
        // For now, we manually initialize a few words and fill the rest with 0.
        rom[0] = 32'h20100005; // e.g. ADDI x1,x0,5 (hex example)
        // … you can fill rom[1], rom[2], etc., here …

        // Fill the rest with NOP (all zeros)
        for (i = 10; i < 256; i = i + 1) begin
            rom[i] = 32'b0;
        end
    end

    always @(*) begin
        instr = rom[addr[9:2]]; // instruction index = addr/4
    end
endmodule
