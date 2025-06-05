// issue_queue.v
// Small issue queue used for out-of-order scheduling demonstration.
// The queue previously issued entries strictly in program order.  It now
// tracks simple operand readiness so instructions may issue once their
// inputs are available.
module issue_queue(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [31:0] instr,
    input  wire [5:0]  phys_src1,
    input  wire [5:0]  phys_src2,
    input  wire [5:0]  phys_dest,
    input  wire        wakeup_valid,
    input  wire [5:0]  wakeup_phys,
    output wire        ready
);
    reg [31:0] instr_q [0:31];
    reg [5:0]  src1_q [0:31], src2_q [0:31], dest_q [0:31];
    reg        src1_ready[0:31], src2_ready[0:31];
    reg        valid_q[0:31];
    reg [5:0]  head, tail;

    wire [5:0] issue_idx;
    assign ready = find_ready(issue_idx);

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head <= 0; tail <= 0;
            for (i = 0; i < 32; i = i + 1) begin
                valid_q[i] <= 0;
                src1_ready[i] <= 0;
                src2_ready[i] <= 0;
            end
        end else begin
            // enqueue decoded instruction if queue not full
            if (!valid_q[tail]) begin
                instr_q[tail] <= instr;
                src1_q[tail]  <= phys_src1;
                src2_q[tail]  <= phys_src2;
                dest_q[tail]  <= phys_dest;
                src1_ready[tail] <= 0;
                src2_ready[tail] <= 0;
                valid_q[tail] <= 1;
                tail <= tail + 1;
            end

            // wakeup broadcast
            if (wakeup_valid) begin
                for (i = 0; i < 32; i = i + 1) begin
                    if (valid_q[i]) begin
                        if (src1_q[i] == wakeup_phys) src1_ready[i] <= 1;
                        if (src2_q[i] == wakeup_phys) src2_ready[i] <= 1;
                    end
                end
            end

            // stub: mark operands of current head ready after a short delay
            if (valid_q[head] && !(src1_ready[head] && src2_ready[head])) begin
                src1_ready[head] <= 1;
                src2_ready[head] <= 1;
            end

            // issue the first ready entry
            if (ready) begin
                valid_q[issue_idx] <= 0;
                head <= issue_idx + 1;
            end
        end
    end

    function automatic bit find_ready(output [5:0] idx);
        integer j;
        begin
            find_ready = 0;
            idx = head;
            for (j = 0; j < 32; j = j + 1) begin
                if (valid_q[j] && src1_ready[j] && src2_ready[j]) begin
                    find_ready = 1;
                    idx = j;
                    disable find_ready;
                end
            end
        end
    endfunction
endmodule
