// cpu64_superscalar.v
// Simplified dual-issue superscalar CPU with a deeper pipeline.
// This module demonstrates two parallel pipelines with shared register
// file and memory. It reuses the single-issue pipeline components and
// adds minimal cross-lane hazard checking.

`timescale 1ns/1ps
module cpu64_superscalar(
    input  wire clk,
    input  wire rst_n
);
    // Program counter increments by 8 bytes (two instructions) each cycle
    reg [63:0] PC;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            PC <= 64'b0;
        end else begin
            PC <= PC + 64'd8;
        end
    end

    // Fetch two instructions
    wire [63:0] if_pc0  = PC;
    wire [63:0] if_pc1  = PC + 64'd4;
    wire [63:0] if_pc_plus8 = PC + 64'd8;
    wire [31:0] if_instr0, if_instr1;

    imem_superscalar imem_u(
        .addr0(if_pc0),
        .addr1(if_pc1),
        .instr0(if_instr0),
        .instr1(if_instr1)
    );

    // IF/ID pipeline registers for each lane
    wire [63:0] id_pc_plus4_0, id_pc_plus4_1;
    wire [31:0] id_instr0, id_instr1;

    IF_ID if_id_0(
        .clk(clk), .rst_n(rst_n), .stall(1'b0),
        .if_pc_plus4(if_pc0 + 64'd4), .if_instr(if_instr0),
        .id_pc_plus4(id_pc_plus4_0), .id_instr(id_instr0)
    );
    IF_ID if_id_1(
        .clk(clk), .rst_n(rst_n), .stall(1'b0),
        .if_pc_plus4(if_pc1 + 64'd4), .if_instr(if_instr1),
        .id_pc_plus4(id_pc_plus4_1), .id_instr(id_instr1)
    );

    // Decode fields for each lane
    wire [5:0] id_opcode [1:0];
    wire [4:0] id_rs1 [1:0];
    wire [4:0] id_rs2 [1:0];
    wire [4:0] id_rd  [1:0];
    wire [5:0] id_funct[1:0];
    wire [15:0] id_imm16[1:0];

    assign id_opcode[0] = id_instr0[31:26];
    assign id_opcode[1] = id_instr1[31:26];
    assign id_rs1[0]    = id_instr0[25:21];
    assign id_rs1[1]    = id_instr1[25:21];
    assign id_rs2[0]    = id_instr0[20:16];
    assign id_rs2[1]    = id_instr1[20:16];
    assign id_rd[0]     = (id_opcode[0]==6'b000000) ? id_instr0[15:11] : id_instr0[20:16];
    assign id_rd[1]     = (id_opcode[1]==6'b000000) ? id_instr1[15:11] : id_instr1[20:16];
    assign id_funct[0]  = id_instr0[5:0];
    assign id_funct[1]  = id_instr1[5:0];
    assign id_imm16[0]  = id_instr0[15:0];
    assign id_imm16[1]  = id_instr1[15:0];

    // Register file shared between lanes
    wire [63:0] id_reg_data1_0, id_reg_data2_0;
    wire [63:0] id_reg_data1_1, id_reg_data2_1;

    // WB stage wires per lane
    wire [63:0] wb_data0, wb_data1;
    wire [4:0]  wb_rd0, wb_rd1;
    wire        wb_reg_write0, wb_reg_write1;

    regfile64_superscalar rf_u(
        .clk(clk), .rst_n(rst_n),
        .ra1_0(id_rs1[0]), .ra2_0(id_rs2[0]),
        .rd1_0(id_reg_data1_0), .rd2_0(id_reg_data2_0),
        .ra1_1(id_rs1[1]), .ra2_1(id_rs2[1]),
        .rd1_1(id_reg_data1_1), .rd2_1(id_reg_data2_1),
        .wb_reg_write0(wb_reg_write0), .wb_rd0(wb_rd0), .wb_data0(wb_data0),
        .wb_reg_write1(wb_reg_write1), .wb_rd1(wb_rd1), .wb_data1(wb_data1)
    );

    // Control units per lane
    wire        id_reg_write [1:0];
    wire        id_alu_src   [1:0];
    wire [2:0]  id_alu_op    [1:0];
    wire        id_mem_read  [1:0];
    wire        id_mem_write [1:0];
    wire        id_mem_to_reg[1:0];
    wire        id_branch    [1:0];

    control ctrl0(
        .opcode(id_opcode[0]), .funct(id_funct[0]),
        .reg_write(id_reg_write[0]), .alu_src(id_alu_src[0]),
        .alu_op(id_alu_op[0]), .mem_read(id_mem_read[0]),
        .mem_write(id_mem_write[0]), .mem_to_reg(id_mem_to_reg[0]),
        .branch(id_branch[0])
    );
    control ctrl1(
        .opcode(id_opcode[1]), .funct(id_funct[1]),
        .reg_write(id_reg_write[1]), .alu_src(id_alu_src[1]),
        .alu_op(id_alu_op[1]), .mem_read(id_mem_read[1]),
        .mem_write(id_mem_write[1]), .mem_to_reg(id_mem_to_reg[1]),
        .branch(id_branch[1])
    );

    // Hazard: stall lane1 if it depends on a load in lane0
    wire stall_lane1;
    hazard_unit_superscalar hz_ss(
        .lane0_mem_read(id_mem_read[0]),
        .lane0_rd(id_rd[0]),
        .lane1_rs1(id_rs1[1]),
        .lane1_rs2(id_rs2[1]),
        .stall_lane1(stall_lane1)
    );

    // ID/EX registers per lane
    wire [63:0] ex_pc_plus4 [1:0];
    wire [4:0]  ex_rs1 [1:0];
    wire [4:0]  ex_rs2 [1:0];
    wire [4:0]  ex_rd  [1:0];
    wire [5:0]  ex_opcode [1:0];
    wire [5:0]  ex_funct  [1:0];
    wire [15:0] ex_imm16  [1:0];
    wire [63:0] ex_reg_data1 [1:0];
    wire [63:0] ex_reg_data2 [1:0];
    wire        ex_reg_write [1:0];
    wire        ex_alu_src   [1:0];
    wire [2:0]  ex_alu_op    [1:0];
    wire        ex_mem_read  [1:0];
    wire        ex_mem_write [1:0];
    wire        ex_mem_to_reg[1:0];
    wire        ex_branch    [1:0];

    ID_EX id_ex_0(
        .clk(clk), .rst_n(rst_n), .stall(1'b0),
        .id_pc_plus4(id_pc_plus4_0), .id_rs1(id_rs1[0]), .id_rs2(id_rs2[0]),
        .id_rd(id_rd[0]), .id_opcode(id_opcode[0]), .id_funct(id_funct[0]),
        .id_imm16(id_imm16[0]), .id_reg_data1(id_reg_data1_0), .id_reg_data2(id_reg_data2_0),
        .id_reg_write(id_reg_write[0]), .id_alu_src(id_alu_src[0]), .id_alu_op(id_alu_op[0]),
        .id_mem_read(id_mem_read[0]), .id_mem_write(id_mem_write[0]),
        .id_mem_to_reg(id_mem_to_reg[0]), .id_branch(id_branch[0]),
        .ex_pc_plus4(ex_pc_plus4[0]), .ex_rs1(ex_rs1[0]), .ex_rs2(ex_rs2[0]),
        .ex_rd(ex_rd[0]), .ex_opcode(ex_opcode[0]), .ex_funct(ex_funct[0]), .ex_imm16(ex_imm16[0]),
        .ex_reg_data1(ex_reg_data1[0]), .ex_reg_data2(ex_reg_data2[0]),
        .ex_reg_write(ex_reg_write[0]), .ex_alu_src(ex_alu_src[0]), .ex_alu_op(ex_alu_op[0]),
        .ex_mem_read(ex_mem_read[0]), .ex_mem_write(ex_mem_write[0]),
        .ex_mem_to_reg(ex_mem_to_reg[0]), .ex_branch(ex_branch[0])
    );

    ID_EX id_ex_1(
        .clk(clk), .rst_n(rst_n), .stall(stall_lane1),
        .id_pc_plus4(id_pc_plus4_1), .id_rs1(id_rs1[1]), .id_rs2(id_rs2[1]),
        .id_rd(id_rd[1]), .id_opcode(id_opcode[1]), .id_funct(id_funct[1]),
        .id_imm16(id_imm16[1]), .id_reg_data1(id_reg_data1_1), .id_reg_data2(id_reg_data2_1),
        .id_reg_write(id_reg_write[1]), .id_alu_src(id_alu_src[1]), .id_alu_op(id_alu_op[1]),
        .id_mem_read(id_mem_read[1]), .id_mem_write(id_mem_write[1]),
        .id_mem_to_reg(id_mem_to_reg[1]), .id_branch(id_branch[1]),
        .ex_pc_plus4(ex_pc_plus4[1]), .ex_rs1(ex_rs1[1]), .ex_rs2(ex_rs2[1]),
        .ex_rd(ex_rd[1]), .ex_opcode(ex_opcode[1]), .ex_funct(ex_funct[1]), .ex_imm16(ex_imm16[1]),
        .ex_reg_data1(ex_reg_data1[1]), .ex_reg_data2(ex_reg_data2[1]),
        .ex_reg_write(ex_reg_write[1]), .ex_alu_src(ex_alu_src[1]), .ex_alu_op(ex_alu_op[1]),
        .ex_mem_read(ex_mem_read[1]), .ex_mem_write(ex_mem_write[1]),
        .ex_mem_to_reg(ex_mem_to_reg[1]), .ex_branch(ex_branch[1])
    );

    // EX stage per lane (no forwarding implemented)
    wire [63:0] ex_imm64_0 = {{48{ex_imm16[0][15]}}, ex_imm16[0]};
    wire [63:0] ex_imm64_1 = {{48{ex_imm16[1][15]}}, ex_imm16[1]};
    wire [63:0] ex_alu_in2_0 = ex_alu_src[0] ? ex_imm64_0 : ex_reg_data2[0];
    wire [63:0] ex_alu_in2_1 = ex_alu_src[1] ? ex_imm64_1 : ex_reg_data2[1];
    wire [63:0] ex_alu_result0, ex_alu_result1;
    wire        ex_zero0, ex_zero1;

    alu64 alu0(.a(ex_reg_data1[0]), .b(ex_alu_in2_0), .alu_op(ex_alu_op[0]), .result(ex_alu_result0), .zero(ex_zero0));
    alu64 alu1(.a(ex_reg_data1[1]), .b(ex_alu_in2_1), .alu_op(ex_alu_op[1]), .result(ex_alu_result1), .zero(ex_zero1));

    // EX/MEM registers
    wire [63:0] mem_pc_plus4 [1:0];
    wire [63:0] mem_alu_result [1:0];
    wire [63:0] mem_reg_data2 [1:0];
    wire [4:0]  mem_rd [1:0];
    wire        mem_zero [1:0];
    wire        mem_reg_write [1:0];
    wire        mem_mem_read  [1:0];
    wire        mem_mem_write [1:0];
    wire        mem_mem_to_reg[1:0];
    wire        mem_branch    [1:0];
    wire [63:0] mem_branch_target [1:0];

    wire [63:0] ex_branch_target0 = ex_pc_plus4[0] + (ex_imm64_0 << 2);
    wire [63:0] ex_branch_target1 = ex_pc_plus4[1] + (ex_imm64_1 << 2);

    EX_MEM ex_mem_0(
        .clk(clk), .rst_n(rst_n),
        .ex_pc_plus4(ex_pc_plus4[0]), .ex_alu_result(ex_alu_result0), .ex_reg_data2(ex_reg_data2[0]),
        .ex_rd(ex_rd[0]), .ex_zero(ex_zero0), .ex_reg_write(ex_reg_write[0]),
        .ex_mem_read(ex_mem_read[0]), .ex_mem_write(ex_mem_write[0]), .ex_mem_to_reg(ex_mem_to_reg[0]),
        .ex_branch(ex_branch[0]), .ex_branch_target(ex_branch_target0),
        .mem_pc_plus4(mem_pc_plus4[0]), .mem_alu_result(mem_alu_result[0]), .mem_reg_data2(mem_reg_data2[0]),
        .mem_rd(mem_rd[0]), .mem_zero(mem_zero[0]), .mem_reg_write(mem_reg_write[0]), .mem_mem_read(mem_mem_read[0]),
        .mem_mem_write(mem_mem_write[0]), .mem_mem_to_reg(mem_mem_to_reg[0]),
        .mem_branch(mem_branch[0]), .mem_branch_target(mem_branch_target[0])
    );

    EX_MEM ex_mem_1(
        .clk(clk), .rst_n(rst_n),
        .ex_pc_plus4(ex_pc_plus4[1]), .ex_alu_result(ex_alu_result1), .ex_reg_data2(ex_reg_data2[1]),
        .ex_rd(ex_rd[1]), .ex_zero(ex_zero1), .ex_reg_write(ex_reg_write[1]),
        .ex_mem_read(ex_mem_read[1]), .ex_mem_write(ex_mem_write[1]), .ex_mem_to_reg(ex_mem_to_reg[1]),
        .ex_branch(ex_branch[1]), .ex_branch_target(ex_branch_target1),
        .mem_pc_plus4(mem_pc_plus4[1]), .mem_alu_result(mem_alu_result[1]), .mem_reg_data2(mem_reg_data2[1]),
        .mem_rd(mem_rd[1]), .mem_zero(mem_zero[1]), .mem_reg_write(mem_reg_write[1]), .mem_mem_read(mem_mem_read[1]),
        .mem_mem_write(mem_mem_write[1]), .mem_mem_to_reg(mem_mem_to_reg[1]),
        .mem_branch(mem_branch[1]), .mem_branch_target(mem_branch_target[1])
    );

    // Data memory shared
    wire [63:0] mem_read_data0, mem_read_data1;
    dmem_pipelined dmem0(.clk(clk), .rst_n(rst_n), .mem_read(mem_mem_read[0]), .mem_write(mem_mem_write[0]), .addr(mem_alu_result[0]), .write_data(mem_reg_data2[0]), .read_data(mem_read_data0));
    dmem_pipelined dmem1(.clk(clk), .rst_n(rst_n), .mem_read(mem_mem_read[1]), .mem_write(mem_mem_write[1]), .addr(mem_alu_result[1]), .write_data(mem_reg_data2[1]), .read_data(mem_read_data1));

    // MEM/WB registers
    wire [63:0] wb_read_data0, wb_alu_result0;
    wire wb_mem_to_reg0, wb_mem_to_reg1;
    wire [63:0] wb_read_data1, wb_alu_result1;

    MEM_WB mem_wb_0(
        .clk(clk), .rst_n(rst_n),
        .mem_read_data(mem_read_data0), .mem_alu_result(mem_alu_result[0]), .mem_rd(mem_rd[0]),
        .mem_reg_write(mem_reg_write[0]), .mem_mem_to_reg(mem_mem_to_reg[0]),
        .wb_read_data(wb_read_data0), .wb_alu_result(wb_alu_result0), .wb_rd(wb_rd0),
        .wb_reg_write(wb_reg_write0), .wb_mem_to_reg(wb_mem_to_reg0)
    );
    MEM_WB mem_wb_1(
        .clk(clk), .rst_n(rst_n),
        .mem_read_data(mem_read_data1), .mem_alu_result(mem_alu_result[1]), .mem_rd(mem_rd[1]),
        .mem_reg_write(mem_reg_write[1]), .mem_mem_to_reg(mem_mem_to_reg[1]),
        .wb_read_data(wb_read_data1), .wb_alu_result(wb_alu_result1), .wb_rd(wb_rd1),
        .wb_reg_write(wb_reg_write1), .wb_mem_to_reg(wb_mem_to_reg1)
    );

    // Writeback results for register file
    assign wb_data0 = wb_mem_to_reg0 ? wb_read_data0 : wb_alu_result0;
    assign wb_data1 = wb_mem_to_reg1 ? wb_read_data1 : wb_alu_result1;

endmodule
