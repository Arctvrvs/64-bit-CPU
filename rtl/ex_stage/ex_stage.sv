// ex_stage.sv - Execution stage wrapper with simple FU pipelines
//
// Purpose: Accept up to eight issued micro-ops and route them to
// placeholder functional units. Each functional unit has a fixed
// latency and limited number of pipelines. Results are broadcast on
// the writeback bus when ready. The module also reports the number of
// free pipelines for each unit so the issue queue knows what can be
// dispatched next cycle.

module ex_stage(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       flush_i,

    input  logic [7:0] issue_valid,
    input  logic [63:0] op1       [7:0],
    input  logic [63:0] op2       [7:0],
    input  logic [63:0] op3       [7:0],
    input  logic [63:0] pc        [7:0],
    input  logic [2:0]  branch_ctrl [7:0],
    input  logic [6:0]  dest_phys [7:0],
    input  logic [7:0]  rob_idx   [7:0],
    input  logic [3:0]  fu_type   [7:0], // 0=int,1=mul,2=vec,3=mem,4=branch
    input  logic [7:0]  pred_taken,
    input  logic [63:0] pred_target [7:0],

    output logic [1:0] fu_int_free_o,
    output logic       fu_mul_free_o,
    output logic [1:0] fu_vec_free_o,
    output logic [1:0] fu_mem_free_o,
    output logic       fu_branch_free_o,

    output logic [7:0] br_mispredict,
    output logic [63:0] br_target [7:0],

    output logic [7:0] wb_valid,
    output logic [63:0] wb_data [7:0],
    output logic [6:0] wb_dest [7:0],
    output logic [7:0] wb_rob_idx [7:0]
);

    typedef struct packed {
        logic       valid;
        int         countdown;
        logic [63:0] data;
        logic [6:0]  dest;
        logic [7:0]  rob;
        logic        br_misp;
        logic [63:0] br_tgt;
    } slot_t;

    slot_t int_slots [2];
    slot_t vec_slots [2];
    slot_t mem_slots [2];
    slot_t branch_slot;
    slot_t mul_slot;

    function void clear_slot(ref slot_t s);
        s.valid = 1'b0;
        s.countdown = 0;
        s.data = '0;
        s.dest = '0;
        s.rob = '0;
        s.br_misp = 1'b0;
        s.br_tgt = '0;
    endfunction

    // reset / flush
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || flush_i) begin
            for (int i=0;i<2;i++) begin
                clear_slot(int_slots[i]);
                clear_slot(vec_slots[i]);
                clear_slot(mem_slots[i]);
            end
            clear_slot(branch_slot);
            clear_slot(mul_slot);
        end else begin
            // advance pipelines
            for (int i=0;i<2;i++) begin
                if (int_slots[i].valid && int_slots[i].countdown>0)
                    int_slots[i].countdown--;
                if (vec_slots[i].valid && vec_slots[i].countdown>0)
                    vec_slots[i].countdown--;
                if (mem_slots[i].valid && mem_slots[i].countdown>0)
                    mem_slots[i].countdown--;
            end
            if (mul_slot.valid && mul_slot.countdown>0)
                mul_slot.countdown--;
            if (branch_slot.valid && branch_slot.countdown>0)
                branch_slot.countdown--;

            // capture new issues
            for (int j=0;j<8;j++) begin
                if (!issue_valid[j])
                    continue;
                case(fu_type[j])
                    0: begin // int ALU
                        if (!int_slots[0].valid) begin
                            int_slots[0].valid      <= 1'b1;
                            int_slots[0].countdown  <= 1;
                            int_slots[0].data       <= op1[j] + op2[j];
                            int_slots[0].dest       <= dest_phys[j];
                            int_slots[0].rob        <= rob_idx[j];
                            int_slots[0].br_misp    <= 1'b0;
                            int_slots[0].br_tgt     <= '0;
                        end else if (!int_slots[1].valid) begin
                            int_slots[1].valid      <= 1'b1;
                            int_slots[1].countdown  <= 1;
                            int_slots[1].data       <= op1[j] + op2[j];
                            int_slots[1].dest       <= dest_phys[j];
                            int_slots[1].rob        <= rob_idx[j];
                            int_slots[1].br_misp    <= 1'b0;
                            int_slots[1].br_tgt     <= '0;
                        end
                    end
                    1: begin // mul/div (mul only here)
                        if (!mul_slot.valid) begin
                            mul_slot.valid      <= 1'b1;
                            mul_slot.countdown  <= 3;
                            mul_slot.data       <= op1[j] * op2[j];
                            mul_slot.dest       <= dest_phys[j];
                            mul_slot.rob        <= rob_idx[j];
                            mul_slot.br_misp    <= 1'b0;
                            mul_slot.br_tgt     <= '0;
                        end
                    end
                    2: begin // vector FMA
                        if (!vec_slots[0].valid) begin
                            vec_slots[0].valid     <= 1'b1;
                            vec_slots[0].countdown <= 5;
                            vec_slots[0].data      <= (op1[j]*op2[j]) + op3[j];
                            vec_slots[0].dest      <= dest_phys[j];
                            vec_slots[0].rob       <= rob_idx[j];
                            vec_slots[0].br_misp   <= 1'b0;
                            vec_slots[0].br_tgt    <= '0;
                        end else if (!vec_slots[1].valid) begin
                            vec_slots[1].valid     <= 1'b1;
                            vec_slots[1].countdown <= 5;
                            vec_slots[1].data      <= (op1[j]*op2[j]) + op3[j];
                            vec_slots[1].dest      <= dest_phys[j];
                            vec_slots[1].rob       <= rob_idx[j];
                            vec_slots[1].br_misp   <= 1'b0;
                            vec_slots[1].br_tgt    <= '0;
                        end
                    end
                    3: begin // memory
                        if (!mem_slots[0].valid) begin
                            mem_slots[0].valid     <= 1'b1;
                            mem_slots[0].countdown <= 2;
                            mem_slots[0].data      <= op2[j];
                            mem_slots[0].dest      <= dest_phys[j];
                            mem_slots[0].rob       <= rob_idx[j];
                            mem_slots[0].br_misp   <= 1'b0;
                            mem_slots[0].br_tgt    <= '0;
                        end else if (!mem_slots[1].valid) begin
                            mem_slots[1].valid     <= 1'b1;
                            mem_slots[1].countdown <= 2;
                            mem_slots[1].data      <= op2[j];
                            mem_slots[1].dest      <= dest_phys[j];
                            mem_slots[1].rob       <= rob_idx[j];
                            mem_slots[1].br_misp   <= 1'b0;
                            mem_slots[1].br_tgt    <= '0;
                        end
                    end
                    default: begin // branch
                        if (!branch_slot.valid) begin
                            logic taken;
                            logic [63:0] tgt;
                            case(branch_ctrl[j])
                                3'd0: taken = (op1[j]==op2[j]);
                                3'd1: taken = (op1[j]!=op2[j]);
                                3'd2: taken = ($signed(op1[j]) < $signed(op2[j]));
                                3'd3: taken = ($signed(op1[j]) >= $signed(op2[j]));
                                3'd4: taken = (op1[j] < op2[j]);
                                3'd5: taken = (op1[j] >= op2[j]);
                                3'd6: taken = 1'b1;
                                3'd7: taken = 1'b1;
                                default: taken = 1'b0;
                            endcase
                            if (branch_ctrl[j]==3'd7)
                                tgt = (op1[j]+op3[j]) & 64'hFFFF_FFFF_FFFF_FFFE;
                            else
                                tgt = pc[j] + op3[j];
                            logic [63:0] actual = taken ? tgt : pc[j] + 64'd4;
                            branch_slot.valid     <= 1'b1;
                            branch_slot.countdown <= 1;
                            branch_slot.data      <= 64'd0;
                            branch_slot.dest      <= dest_phys[j];
                            branch_slot.rob       <= rob_idx[j];
                            branch_slot.br_misp   <= (pred_taken[j] != taken) ||
                                (pred_taken[j] && taken && pred_target[j] != actual);
                            branch_slot.br_tgt    <= actual;
                        end
                    end
                endcase
            end

            // produce results
            for (int i=0;i<2;i++) begin
                if (int_slots[i].valid && int_slots[i].countdown==0) begin
                    wb_valid[i]     <= 1'b1;
                    wb_data[i]      <= int_slots[i].data;
                    wb_dest[i]      <= int_slots[i].dest;
                    wb_rob_idx[i]   <= int_slots[i].rob;
                    br_mispredict[i]<= 1'b0;
                    br_target[i]    <= 64'd0;
                    clear_slot(int_slots[i]);
                end else begin
                    wb_valid[i]     <= 1'b0;
                    br_mispredict[i]<= 1'b0;
                    br_target[i]    <= 64'd0;
                end
            end
            if (mul_slot.valid && mul_slot.countdown==0) begin
                wb_valid[2]     <= 1'b1;
                wb_data[2]      <= mul_slot.data;
                wb_dest[2]      <= mul_slot.dest;
                wb_rob_idx[2]   <= mul_slot.rob;
                br_mispredict[2]<= 1'b0;
                br_target[2]    <= 64'd0;
                clear_slot(mul_slot);
            end else begin
                wb_valid[2]     <= 1'b0;
                br_mispredict[2]<= 1'b0;
                br_target[2]    <= 64'd0;
            end
            for (int i=0;i<2;i++) begin
                int idx = 3+i;
                if (vec_slots[i].valid && vec_slots[i].countdown==0) begin
                    wb_valid[idx]   <= 1'b1;
                    wb_data[idx]    <= vec_slots[i].data;
                    wb_dest[idx]    <= vec_slots[i].dest;
                    wb_rob_idx[idx] <= vec_slots[i].rob;
                    br_mispredict[idx] <= 1'b0;
                    br_target[idx]  <= 64'd0;
                    clear_slot(vec_slots[i]);
                end else begin
                    wb_valid[idx] <= 1'b0;
                    br_mispredict[idx] <= 1'b0;
                    br_target[idx] <= 64'd0;
                end
            end
            for (int i=0;i<2;i++) begin
                int idx = 5+i;
                if (mem_slots[i].valid && mem_slots[i].countdown==0) begin
                    wb_valid[idx]   <= 1'b1;
                    wb_data[idx]    <= mem_slots[i].data;
                    wb_dest[idx]    <= mem_slots[i].dest;
                    wb_rob_idx[idx] <= mem_slots[i].rob;
                    br_mispredict[idx] <= 1'b0;
                    br_target[idx]  <= 64'd0;
                    clear_slot(mem_slots[i]);
                end else begin
                    wb_valid[idx] <= 0;
                    br_mispredict[idx] <= 0;
                    br_target[idx] <= 0;
                end
            end
            if (branch_slot.valid && branch_slot.countdown==0) begin
                wb_valid[7]     <= 1'b1;
                wb_data[7]      <= branch_slot.data;
                wb_dest[7]      <= branch_slot.dest;
                wb_rob_idx[7]   <= branch_slot.rob;
                br_mispredict[7]<= branch_slot.br_misp;
                br_target[7]    <= branch_slot.br_tgt;
                clear_slot(branch_slot);
            end else begin
                wb_valid[7]     <= 1'b0;
                br_mispredict[7]<= 1'b0;
                br_target[7]    <= 64'd0;
            end
        end
    end

    assign fu_int_free_o    = {~int_slots[1].valid, ~int_slots[0].valid};
    assign fu_mul_free_o    = ~mul_slot.valid;
    assign fu_vec_free_o    = {~vec_slots[1].valid, ~vec_slots[0].valid};
    assign fu_mem_free_o    = {~mem_slots[1].valid, ~mem_slots[0].valid};
    assign fu_branch_free_o = ~branch_slot.valid;

endmodule
