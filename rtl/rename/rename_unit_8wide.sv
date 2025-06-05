// rename_unit_8wide.sv - Register renaming logic for 8-wide decode
//
// Purpose: Map architectural registers to physical registers using
// a free-list and rename table. Allocates up to eight instructions
// per cycle. This is a simplified placeholder implementation without
// branch checkpointing or mispredict recovery.

module rename_unit_8wide (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  valid_in,
    input  logic [4:0]  rs1_arch_i [7:0],
    input  logic [4:0]  rs2_arch_i [7:0],
    input  logic [4:0]  rd_arch_i  [7:0],
    input  logic        can_allocate_rob8,
    input  logic        can_allocate_rs8,
    output logic [6:0]  rs1_phys_o [7:0],
    output logic [6:0]  rs2_phys_o [7:0],
    output logic [6:0]  rd_phys_o  [7:0],
    output logic [6:0]  old_rd_phys_o [7:0],
    output logic [7:0]  rename_valid_o,
    output logic [6:0]  free_list_count_o
);

    parameter int PHYS_REGS = 128;
    parameter int ARCH_REGS = 32;
    parameter int FREE_LIST_SIZE = PHYS_REGS - ARCH_REGS;

    // Mapping table arch -> phys
    logic [6:0] arch_to_phys [ARCH_REGS-1:0];

    // Free list implemented as circular buffer
    logic [6:0] free_list   [FREE_LIST_SIZE-1:0];
    logic [6:0] free_head, free_tail;
    logic [6:0] free_count;

    assign free_list_count_o = free_count;

    // Initial setup
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < ARCH_REGS; i++) begin
                arch_to_phys[i] <= i[6:0];
            end
            for (int j = 0; j < FREE_LIST_SIZE; j++) begin
                free_list[j] <= ARCH_REGS + j;
            end
            free_head <= 0;
            free_tail <= 0;
            free_count <= FREE_LIST_SIZE[6:0];
        end else begin
            // Allocate new physical registers when enabled
            if (can_allocate_rob8 && can_allocate_rs8 && free_count >= 8) begin
                for (int k = 0; k < 8; k++) begin
                    if (valid_in[k]) begin
                        old_rd_phys_o[k] <= arch_to_phys[rd_arch_i[k]];
                        rd_phys_o[k]     <= free_list[free_head];
                        arch_to_phys[rd_arch_i[k]] <= free_list[free_head];
                        free_head <= free_head + 1;
                        free_count <= free_count - 1;
                        rename_valid_o[k] <= 1'b1;
                    end else begin
                        old_rd_phys_o[k] <= arch_to_phys[rd_arch_i[k]];
                        rd_phys_o[k]     <= arch_to_phys[rd_arch_i[k]];
                        rename_valid_o[k] <= 1'b0;
                    end
                    rs1_phys_o[k] <= arch_to_phys[rs1_arch_i[k]];
                    rs2_phys_o[k] <= arch_to_phys[rs2_arch_i[k]];
                end
            end else begin
                // Not enough resources: outputs invalid
                for (int m = 0; m < 8; m++) begin
                    rs1_phys_o[m]     <= arch_to_phys[rs1_arch_i[m]];
                    rs2_phys_o[m]     <= arch_to_phys[rs2_arch_i[m]];
                    rd_phys_o[m]      <= arch_to_phys[rd_arch_i[m]];
                    old_rd_phys_o[m]  <= arch_to_phys[rd_arch_i[m]];
                    rename_valid_o[m] <= 1'b0;
                end
            end
        end
    end

endmodule
