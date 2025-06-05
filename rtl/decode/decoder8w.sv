// decoder8w.sv - 8-wide RISC-V instruction decoder
//
// Purpose: Decode up to eight 32-bit instruction words per cycle and
// output the basic fields required by downstream rename logic. This
// is a simplified placeholder that supports a minimal subset of RV64I
// instructions for early integration testing.

module decoder8w (
    input  logic         clk,
    input  logic         rst_n,
    input  logic [31:0]  instr_i [7:0],
    input  logic [63:0]  pc_i    [7:0],
    output logic         valid_o    [7:0],
    output logic [4:0]   rd_arch_o  [7:0],
    output logic [4:0]   rs1_arch_o [7:0],
    output logic [4:0]   rs2_arch_o [7:0],
    output logic [63:0]  imm_o      [7:0],
    output logic [2:0]   func3_o    [7:0],
    output logic [6:0]   func7_o    [7:0],
    output logic         is_branch_o[7:0],
    output logic [2:0]   exception_o[7:0]
);

    // Simple combinational decode for a subset of instructions
    always_comb begin
        for (int i = 0; i < 8; i++) begin
            logic [6:0] opcode;
            opcode = instr_i[i][6:0];
            valid_o[i]      = 1'b1;
            rd_arch_o[i]    = instr_i[i][11:7];
            rs1_arch_o[i]   = instr_i[i][19:15];
            rs2_arch_o[i]   = instr_i[i][24:20];
            func3_o[i]      = instr_i[i][14:12];
            func7_o[i]      = instr_i[i][31:25];
            imm_o[i]        = 64'd0;
            is_branch_o[i]  = (opcode == 7'b1100011);
            exception_o[i]  = 3'b000;

            // Handle I-type immediate as a simple example
            if (opcode == 7'b0010011 || opcode == 7'b0000011) begin
                imm_o[i] = {{52{instr_i[i][31]}}, instr_i[i][31:20]};
            end
        end
    end
endmodule
