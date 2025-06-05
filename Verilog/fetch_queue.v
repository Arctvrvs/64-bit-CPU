// fetch_queue.v
//
// A tiny two-entry FIFO used by the out-of-order core.  It fetches
// instructions from the on-chip ROM and buffers them so that the
// decode/rename stage can run independently from the fetch stage.
// When the queue is not full a new instruction is fetched each cycle
// using the provided PC.  The head of the queue is presented on the
// `pc_out`/`instr_out` ports and is popped when `dequeue` is asserted.
module fetch_queue(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] pc_in,
    input  wire        dequeue,
    output wire [63:0] pc_out,
    output wire [31:0] instr_out,
    output wire        empty,
    output wire        full
);
    // ------------------------------------------------------------------
    // Instruction memory (shared simple ROM from the pipelined design)
    // ------------------------------------------------------------------
    wire [31:0] fetch_instr;
    imem_pipelined imem_u(
        .addr(pc_in),
        .instr(fetch_instr)
    );

    // Two entry circular buffer
    reg [63:0] pc_fifo   [0:1];
    reg [31:0] instr_fifo[0:1];
    reg [1:0]  head, tail;
    reg [1:0]  count;

    assign empty = (count == 0);
    assign full  = (count == 2);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head  <= 2'b0;
            tail  <= 2'b0;
            count <= 2'b0;
        end else begin
            // Enqueue new instruction if space is available
            if (!full) begin
                pc_fifo[tail]    <= pc_in;
                instr_fifo[tail] <= fetch_instr;
                tail  <= tail + 1'b1;
                count <= count + 1'b1;
            end
            // Dequeue when the consumer is ready
            if (dequeue && !empty) begin
                head  <= head + 1'b1;
                count <= count - 1'b1;
            end
        end
    end

    assign pc_out   = pc_fifo[head];
    assign instr_out= instr_fifo[head];
endmodule
