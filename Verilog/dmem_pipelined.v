// dmem_pipelined.v
module dmem_pipelined (
    input  wire         clk,
    input  wire         rst_n,
    input  wire         mem_read,
    input  wire         mem_write,
    input  wire [63:0]  addr,
    input  wire [63:0]  write_data,
    output reg  [63:0]  read_data
);
    reg [63:0] ram [0:255];
    integer i;

    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            ram[i] = 64'b0;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 256; i = i + 1) begin
                ram[i] <= 64'b0;
            end
            read_data <= 64'b0;
        end else begin
            if (mem_write) begin
                ram[addr[9:3]] <= write_data; // address/8 for 64-bit words
            end
            if (mem_read) begin
                read_data <= ram[addr[9:3]];
            end else begin
                read_data <= 64'b0;
            end
        end
    end
endmodule
