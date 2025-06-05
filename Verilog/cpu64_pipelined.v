// cpu64_pipelined.v
`timescale 1ns/1ps

module cpu64_pipelined (
    input  wire clk,
    input  wire rst_n
);
    // ----- Shared Wires -----
    wire [63:0] if_pc, if_pc_plus4, if_instr;

    // IF/ID pipeline registers
    wire [63:0] id_pc_plus4;
    wire [31:0] id_instr;

    // Decoded fields (ID stage)
    wire [5:0]  id_opcode  = id_instr[31:26];
    wire [4:0]  id_rs1     = id_instr[25:21];
    wire [4:0]  id_rs2     = id_instr[20:16];
    wire [4:0]  id_rd      = (id_opcode == 6'b000000) ? id_instr[15:11] : id_instr[20:16];
    wire [5:0]  id_funct   = id_instr[5:0];
    wire [15:0] id_imm16   = id_instr[15:0];

    // Register fetch (ID stage)
    wire [63:0] id_reg_data1, id_reg_data2;

    // Control signals from ID
    wire        id_reg_write, id_alu_src, id_mem_read, id_mem_write, id_mem_to_reg, id_branch;
    wire [2:0]  id_alu_op;

    // Hazard detection
    wire        stall;
    wire [4:0]  ex_rs1_hz, ex_rs2_hz, ex_rd_hz;
    wire        ex_mem_read_hz;
    
    // Wires feeding ID/EX register
    wire [63:0] ex_pc_plus4;
    wire [4:0]  ex_rs1, ex_rs2, ex_rd;
    wire [5:0]  ex_opcode, ex_funct;
    wire [15:0] ex_imm16;
    wire [63:0] ex_reg_data1, ex_reg_data2;
    wire        ex_reg_write, ex_alu_src, ex_mem_read, ex_mem_write, ex_mem_to_reg, ex_branch;
    wire [2:0]  ex_alu_op;

    // EX stage
    wire [63:0] ex_alu_in1, ex_alu_in2, ex_alu_result;
    wire        ex_zero;
    wire [63:0] ex_branch_target;

    // Wires feeding EX/MEM
    wire [63:0] mem_pc_plus4, mem_alu_result, mem_reg_data2;
    wire [4:0]  mem_rd;
    wire        mem_zero, mem_reg_write, mem_mem_read, mem_mem_write, mem_mem_to_reg, mem_branch;
    wire [63:0] mem_branch_target;

    // Data memory outputs
    wire [63:0] mem_read_data;

    // Wires feeding MEM/WB
    wire [63:0] wb_read_data, wb_alu_result;
    wire [4:0]  wb_rd;
    wire        wb_reg_write, wb_mem_to_reg;

    // Hazard Unit in ID
    hazard_unit hz_u (
        .idex_mem_read(ex_mem_read_hz),
        .idex_rd      (ex_rd_hz),
        .ifid_rs1     (id_rs1),
        .ifid_rs2     (id_rs2),
        .stall        (stall)
    );

    // Forwarding Unit in EX
    wire [1:0] forwardA, forwardB;
    forward_unit fu_u (
        .exmem_reg_write(mem_reg_write),
        .exmem_rd        (mem_rd),
        .memwb_reg_write (wb_reg_write),
        .memwb_rd        (wb_rd),
        .idex_rs1        (ex_rs1),
        .idex_rs2        (ex_rs2),
        .forwardA        (forwardA),
        .forwardB        (forwardB)
    );

    // ----------------------------------------------------------------
    // 1) IF Stage: PC, IMEM, IF/ID register
    // ----------------------------------------------------------------
    // PC register (not pipelined-just a simple flop)
    reg [63:0] PC;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            PC <= 64'b0;
        end else if (!stall) begin
            // If no stall, update PC; if stall, keep same PC
            PC <= (mem_branch && mem_zero) ? mem_branch_target : (PC + 64'd4);
        end
    end

    assign if_pc = PC;
    assign if_pc_plus4 = PC + 64'd4;

    // Instruction Memory (combinational read)
    imem_pipelined imem_u (
        .addr(if_pc),
        .instr(if_instr)
    );

    // IF/ID pipeline register
    IF_ID if_id_u (
        .clk       (clk),
        .rst_n     (rst_n),
        .stall     (stall),
        .if_pc_plus4(if_pc_plus4),
        .if_instr  (if_instr),
        .id_pc_plus4(id_pc_plus4),
        .id_instr  (id_instr)
    );

    // ----------------------------------------------------------------
    // 2) ID Stage: Decode, Register Read, Control, Hazard detection, ID/EX register
    // ----------------------------------------------------------------
    // Register File read
    regfile64_pipelined rf_u (
        .clk        (clk),
        .rst_n      (rst_n),
        .ra1        (id_rs1),
        .ra2        (id_rs2),
        .rd1        (id_reg_data1),
        .rd2        (id_reg_data2),
        .wb_reg_write(wb_reg_write),
        .wb_rd      (wb_rd),
        .wb_data    ((wb_mem_to_reg) ? wb_read_data : wb_alu_result)
    );

    // Control unit (combinational) - outputs ID control signals
    control ctrl_u (
        .opcode    (id_opcode),
        .funct     (id_funct),
        .reg_write (id_reg_write),
        .alu_src   (id_alu_src),
        .alu_op    (id_alu_op),
        .mem_read  (id_mem_read),
        .mem_write (id_mem_write),
        .mem_to_reg(id_mem_to_reg),
        .branch    (id_branch)
    );

    // ID/EX pipeline register (stall if hazard)
    ID_EX id_ex_u (
        .clk         (clk),
        .rst_n       (rst_n),
        .stall       (stall),
        .id_pc_plus4 (id_pc_plus4),
        .id_rs1      (id_rs1),
        .id_rs2      (id_rs2),
        .id_rd       (id_rd),
        .id_opcode   (id_opcode),
        .id_funct    (id_funct),
        .id_imm16    (id_imm16),
        .id_reg_data1(id_reg_data1),
        .id_reg_data2(id_reg_data2),
        .id_reg_write(id_reg_write),
        .id_alu_src  (id_alu_src),
        .id_alu_op   (id_alu_op),
        .id_mem_read (id_mem_read),
        .id_mem_write(id_mem_write),
        .id_mem_to_reg(id_mem_to_reg),
        .id_branch   (id_branch),
        // Outputs to EX
        .ex_pc_plus4  (ex_pc_plus4),
        .ex_rs1       (ex_rs1),
        .ex_rs2       (ex_rs2),
        .ex_rd        (ex_rd),
        .ex_opcode    (ex_opcode),
        .ex_funct     (ex_funct),
        .ex_imm16     (ex_imm16),
        .ex_reg_data1 (ex_reg_data1),
        .ex_reg_data2 (ex_reg_data2),
        .ex_reg_write (ex_reg_write),
        .ex_alu_src   (ex_alu_src),
        .ex_alu_op    (ex_alu_op),
        .ex_mem_read  (ex_mem_read),
        .ex_mem_write (ex_mem_write),
        .ex_mem_to_reg(ex_mem_to_reg),
        .ex_branch    (ex_branch)
    );

    // Expose for hazard detection
    assign ex_mem_read_hz = ex_mem_read;
    assign ex_rd_hz       = ex_rd;
    assign ex_rs1_hz      = ex_rs1;
    assign ex_rs2_hz      = ex_rs2;

    // ----------------------------------------------------------------
    // 3) EX Stage: ALU, Forwarding, EX/MEM register
    // ----------------------------------------------------------------
    // Sign-extend the immediate
    wire [63:0] ex_imm64 = {{48{ex_imm16[15]}}, ex_imm16};

    // Branch target: PC+4 + (imm<<2)
    assign ex_branch_target = ex_pc_plus4 + (ex_imm64 << 2);

    // ALU operand A: usually ex_reg_data1, but if forwarding from MEM/WB or EX/MEM, pick that
    reg [63:0] alu_in1;
    always @(*) begin
        case (forwardA)
            2'b00: alu_in1 = ex_reg_data1;
            2'b10: alu_in1 = mem_alu_result;   // from EX/MEM
            2'b01: alu_in1 = (mem_mem_to_reg ? mem_read_data : wb_alu_result); // from WB
            default: alu_in1 = ex_reg_data1;
        endcase
    end

    // ALU operand B: either ex_reg_data2 (possibly forwarded) or immediate
    reg [63:0] alu_in2_pre;
    always @(*) begin
        case (forwardB)
            2'b00: alu_in2_pre = ex_reg_data2;
            2'b10: alu_in2_pre = mem_alu_result;
            2'b01: alu_in2_pre = (mem_mem_to_reg ? mem_read_data : wb_alu_result);
            default: alu_in2_pre = ex_reg_data2;
        endcase
    end

    wire [63:0] ex_alu_in2 = (ex_alu_src) ? ex_imm64 : alu_in2_pre;

    // ALU itself
    alu64 alu_u (
        .a      (alu_in1),
        .b      (ex_alu_in2),
        .alu_op (ex_alu_op),
        .result (ex_alu_result),
        .zero   (ex_zero)
    );

    // EX/MEM pipeline register
    EX_MEM ex_mem_u (
        .clk            (clk),
        .rst_n          (rst_n),
        .ex_pc_plus4    (ex_pc_plus4),
        .ex_alu_result  (ex_alu_result),
        .ex_reg_data2   (alu_in2_pre),   // store the *un-imm* version for SW
        .ex_rd          (ex_rd),
        .ex_zero        (ex_zero),
        .ex_reg_write   (ex_reg_write),
        .ex_mem_read    (ex_mem_read),
        .ex_mem_write   (ex_mem_write),
        .ex_mem_to_reg  (ex_mem_to_reg),
        .ex_branch      (ex_branch),
        .ex_branch_target(ex_branch_target),
        // Outputs to MEM
        .mem_pc_plus4      (mem_pc_plus4),
        .mem_alu_result    (mem_alu_result),
        .mem_reg_data2     (mem_reg_data2),
        .mem_rd            (mem_rd),
        .mem_zero          (mem_zero),
        .mem_reg_write     (mem_reg_write),
        .mem_mem_read      (mem_mem_read),
        .mem_mem_write     (mem_mem_write),
        .mem_mem_to_reg    (mem_mem_to_reg),
        .mem_branch        (mem_branch),
        .mem_branch_target (mem_branch_target)
    );

    // ----------------------------------------------------------------
    // 4) MEM Stage: Data Memory, Branch decision already made in IF, MEM/WB register
    // ----------------------------------------------------------------
    dmem_pipelined dmem_u (
        .clk        (clk),
        .rst_n      (rst_n),
        .mem_read   (mem_mem_read),
        .mem_write  (mem_mem_write),
        .addr       (mem_alu_result),
        .write_data (mem_reg_data2),
        .read_data  (mem_read_data)
    );

    MEM_WB mem_wb_u (
        .clk           (clk),
        .rst_n         (rst_n),
        .mem_read_data (mem_read_data),
        .mem_alu_result(mem_alu_result),
        .mem_rd        (mem_rd),
        .mem_reg_write (mem_reg_write),
        .mem_mem_to_reg(mem_mem_to_reg),
        // Outputs to WB
        .wb_read_data   (wb_read_data),
        .wb_alu_result  (wb_alu_result),
        .wb_rd          (wb_rd),
        .wb_reg_write   (wb_reg_write),
        .wb_mem_to_reg  (wb_mem_to_reg)
    );

    // Branch resolution: already handled in the IF stage PC update.
    // mem_zero and mem_branch indicate a taken branch. IF checks them and updates PC accordingly.

endmodule
