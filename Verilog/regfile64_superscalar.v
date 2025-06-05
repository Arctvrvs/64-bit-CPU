// regfile64_superscalar.v
// Register file with four read ports and two write ports for superscalar CPU
module regfile64_superscalar(
    input  wire        clk,
    input  wire        rst_n,
    // Read ports for lane 0
    input  wire [4:0]  ra1_0,
    input  wire [4:0]  ra2_0,
    output wire [63:0] rd1_0,
    output wire [63:0] rd2_0,
    // Read ports for lane 1
    input  wire [4:0]  ra1_1,
    input  wire [4:0]  ra2_1,
    output wire [63:0] rd1_1,
    output wire [63:0] rd2_1,
    // Write port lane 0
    input  wire        wb_reg_write0,
    input  wire [4:0]  wb_rd0,
    input  wire [63:0] wb_data0,
    // Write port lane 1
    input  wire        wb_reg_write1,
    input  wire [4:0]  wb_rd1,
    input  wire [63:0] wb_data1
);
    reg [63:0] regs [31:0];
    integer i;

    initial begin
        for (i = 0; i < 32; i = i + 1) begin
            regs[i] = 64'b0;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 32; i = i + 1) begin
                regs[i] <= 64'b0;
            end
        end else begin
            if (wb_reg_write0 && wb_rd0 != 5'b0) regs[wb_rd0] <= wb_data0;
            if (wb_reg_write1 && wb_rd1 != 5'b0) regs[wb_rd1] <= wb_data1;
        end
    end

    assign rd1_0 = (ra1_0 == 5'b0) ? 64'b0 : regs[ra1_0];
    assign rd2_0 = (ra2_0 == 5'b0) ? 64'b0 : regs[ra2_0];
    assign rd1_1 = (ra1_1 == 5'b0) ? 64'b0 : regs[ra1_1];
    assign rd2_1 = (ra2_1 == 5'b0) ? 64'b0 : regs[ra2_1];
endmodule
