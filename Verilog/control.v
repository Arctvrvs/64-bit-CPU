// control.v
module control (
    input  wire [5:0]  opcode,
    input  wire [5:0]  funct,      // only for R-type
    output reg         reg_write,
    output reg         alu_src,    // 0=rs2, 1=imm
    output reg  [2:0]  alu_op,     // 000=ADD,001=SUB,010=AND,011=OR,100=XOR
    output reg         mem_read,
    output reg         mem_write,
    output reg         mem_to_reg, // 0=ALU?Reg; 1=Mem?Reg
    output reg         branch      // BEQ
);
    // Opcodes
    localparam OPC_RTYPE = 6'b000000;
    localparam OPC_ADDI  = 6'b001000;
    localparam OPC_ANDI  = 6'b001100;
    localparam OPC_ORI   = 6'b001101;
    localparam OPC_XORI  = 6'b001110;
    localparam OPC_LW    = 6'b100011;
    localparam OPC_SW    = 6'b101011;
    localparam OPC_BEQ   = 6'b000100;

    // funct codes (for R-type)
    localparam FUNCT_ADD = 6'b100000;
    localparam FUNCT_SUB = 6'b100010;
    localparam FUNCT_AND = 6'b100100;
    localparam FUNCT_OR  = 6'b100101;
    localparam FUNCT_XOR = 6'b100110;
    localparam FUNCT_SLLV= 6'b000100; // shift left logical variable
    localparam FUNCT_SRLV= 6'b000110; // shift right logical variable

    always @(*) begin
        // Default values
        reg_write  = 1'b0;
        alu_src    = 1'b0;
        alu_op     = 3'b000;
        mem_read   = 1'b0;
        mem_write  = 1'b0;
        mem_to_reg = 1'b0;
        branch     = 1'b0;

        case (opcode)
            OPC_RTYPE: begin
                reg_write = 1'b1;
                alu_src   = 1'b0;  // use rs2
                mem_to_reg= 1'b0;  // ALU result
                mem_read  = 1'b0;
                mem_write = 1'b0;
                branch    = 1'b0;
                // Determine ALU op by funct
                case (funct)
                    FUNCT_ADD: alu_op = 3'b000;
                    FUNCT_SUB: alu_op = 3'b001;
                    FUNCT_AND: alu_op = 3'b010;
                    FUNCT_OR:  alu_op = 3'b011;
                    FUNCT_XOR: alu_op = 3'b100;
                    FUNCT_SLLV: alu_op = 3'b101;
                    FUNCT_SRLV: alu_op = 3'b110;
                    default:   alu_op = 3'b000;
                endcase
            end

            OPC_ADDI: begin
                reg_write  = 1'b1;
                alu_src    = 1'b1;  // use immediate
                alu_op     = 3'b000; // ADD
                mem_to_reg = 1'b0;
            end

            OPC_ANDI: begin
                reg_write  = 1'b1;
                alu_src    = 1'b1;
                alu_op     = 3'b010; // AND
                mem_to_reg = 1'b0;
            end

            OPC_ORI: begin
                reg_write  = 1'b1;
                alu_src    = 1'b1;
                alu_op     = 3'b011; // OR
                mem_to_reg = 1'b0;
            end

            OPC_XORI: begin
                reg_write  = 1'b1;
                alu_src    = 1'b1;
                alu_op     = 3'b100; // XOR
                mem_to_reg = 1'b0;
            end

            OPC_LW: begin
                reg_write  = 1'b1;
                alu_src    = 1'b1;   // address = rs1 + imm
                alu_op     = 3'b000; // ADD
                mem_read   = 1'b1;
                mem_to_reg = 1'b1;   // write memory data to reg
            end

            OPC_SW: begin
                alu_src    = 1'b1;  // address = rs1 + imm
                alu_op     = 3'b000; // ADD
                mem_write  = 1'b1;
            end

            OPC_BEQ: begin
                alu_src    = 1'b0;   // compare rs1 vs rs2
                alu_op     = 3'b001; // SUB: result zero if equal
                branch     = 1'b1;
            end

            default: begin
                // NOP or unsupported
            end
        endcase
    end
endmodule
