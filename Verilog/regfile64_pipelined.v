// regfile64_pipelined.v
module regfile64_pipelined (
    input  wire        clk,
    input  wire        rst_n,
    // Read ports (ID stage)
    input  wire [4:0]  ra1,
    input  wire [4:0]  ra2,
    output wire [63:0] rd1,
    output wire [63:0] rd2,
    // Write port (WB stage)
    input  wire        wb_reg_write,
    input  wire [4:0]  wb_rd,
    input  wire [63:0] wb_data
);
    reg [63:0] regs [31:0];
    integer i;

    // Initialize to zero
    initial begin
        for (i = 0; i < 32; i = i + 1) begin
            regs[i] = 64'b0;
        end
    end

    // Write in WB stage on posedge
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 32; i = i + 1) begin
                regs[i] <= 64'b0;
            end
        end else if (wb_reg_write && (wb_rd != 5'b0)) begin
            regs[wb_rd] <= wb_data;
        end
    end

    // Combinational read in ID stage
    assign rd1 = (ra1 == 5'b0) ? 64'b0 : regs[ra1];
    assign rd2 = (ra2 == 5'b0) ? 64'b0 : regs[ra2];
endmodule
