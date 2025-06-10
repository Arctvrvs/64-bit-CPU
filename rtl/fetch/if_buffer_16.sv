// if_buffer_16.sv - Simple instruction fetch FIFO buffer
//
// Purpose: Stores up to 16 instructions (128 bytes) to decouple the
// instruction fetch stage from downstream decode. Two instructions
// (64 bits) may be dequeued each cycle.

// Parameters: none
// Inputs: see port list below
// Outputs: see port list below

(* clock_gating_cell = "yes" *)
module if_buffer_16 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        enq_valid,
    input  logic [63:0] enq_data,
    output logic        enq_ready,
    input  logic        deq_ready,
    output logic        deq_valid,
    output logic [63:0] deq_data
);

    logic [63:0] fifo_mem [15:0];
    logic [4:0]  head, tail, count;

    assign enq_ready = (count < 16);
    assign deq_valid = (count > 0);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head  <= 0;
            tail  <= 0;
            count <= 0;
        end else begin
            if (enq_valid && enq_ready) begin
                fifo_mem[tail] <= enq_data;
                tail <= tail + 1;
                count <= count + 1;
            end
            if (deq_ready && deq_valid) begin
                deq_data <= fifo_mem[head];
                head <= head + 1;
                count <= count - 1;
            end
        end
    end

endmodule
