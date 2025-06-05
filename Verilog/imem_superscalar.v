// imem_superscalar.v
// Dual-issue instruction memory for superscalar CPU
module imem_superscalar(
    input  wire [63:0] addr0,
    input  wire [63:0] addr1,
    output reg  [31:0] instr0,
    output reg  [31:0] instr1
);
    reg [31:0] rom [0:255];
    integer i;

    initial begin
        rom[0] = 32'h20100005; // sample instruction
        for (i = 1; i < 256; i = i + 1) begin
            rom[i] = 32'b0;
        end
    end

    always @(*) begin
        instr0 = rom[addr0[9:2]];
        instr1 = rom[addr1[9:2]];
    end
endmodule
