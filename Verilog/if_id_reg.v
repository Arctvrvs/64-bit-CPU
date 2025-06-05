// if_id_reg.v
module IF_ID (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        stall,          // when asserted, hold the current contents
    input  wire [63:0] if_pc_plus4,    // PC+4 from IF stage
    input  wire [31:0] if_instr,       // fetched instruction
    output reg  [63:0] id_pc_plus4,
    output reg  [31:0] id_instr
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            id_pc_plus4 <= 64'b0;
            id_instr    <= 32'b0;
        end else if (stall) begin
            // hold previous values
            id_pc_plus4 <= id_pc_plus4;
            id_instr    <= id_instr;
        end else begin
            id_pc_plus4 <= if_pc_plus4;
            id_instr    <= if_instr;
        end
    end
endmodule
