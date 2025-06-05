// load_store_buffer.v
// Simple load/store buffer that allows out-of-order memory execution
// while still committing in program order.  The previous version
// generated sequential addresses internally.  It now accepts real
// addresses from the instruction stream and performs a small amount of
// dependency tracking.
module load_store_buffer(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        issue_valid,
    input  wire        is_store,
    input  wire [63:0] addr_in,
    input  wire [63:0] data_in,
    output reg         commit_ready,
    output wire        mem_read,
    output wire        mem_write,
    output wire [63:0] mem_addr,
    output wire [63:0] write_data,
    input  wire [63:0] read_data,
    output reg         miss
);
    // simple 4-entry circular queue
    reg [63:0] addr_q [0:3];
    reg [63:0] data_q [0:3];
    reg        rw_q   [0:3]; // 1=write
    reg        valid_q[0:3];
    reg [1:0]  state_q[0:3]; // 0=waiting 1=exec 2=done
    reg [1:0]  lat_q  [0:3];
    reg [1:0]  head, tail, exec_p;

    wire dep_block;
    assign dep_block = valid_q[exec_p] && state_q[exec_p]==0 && (
        (rw_q[exec_p] && |addr_match_before(exec_p)));

    assign mem_read   = valid_q[exec_p] && !rw_q[exec_p] && state_q[exec_p]==0 && !dep_block;
    assign mem_write  = valid_q[exec_p] &&  rw_q[exec_p] && state_q[exec_p]==0 && !dep_block;
    assign mem_addr   = addr_q[exec_p];
    assign write_data = data_q[exec_p];

    assign commit_ready = valid_q[head] && state_q[head]==2;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head <= 0; tail <= 0; exec_p <= 0;
            for (i = 0; i < 4; i = i + 1) begin
                valid_q[i] <= 0;
                state_q[i] <= 0;
                lat_q[i]   <= 0;
            end
        end else begin
            // Issue a new memory op if queue not full
            if (issue_valid && !valid_q[tail]) begin
                addr_q[tail]  <= addr_in;
                data_q[tail]  <= data_in;
                rw_q[tail]    <= is_store;
                valid_q[tail] <= 1;
                state_q[tail] <= 0;
                lat_q[tail]   <= 2; // fixed latency
                tail          <= tail + 1;
            end

            // Execute any queued op (out of order)
            if (mem_read || mem_write) begin
                state_q[exec_p] <= 1; // executing
                exec_p          <= exec_p + 1;
                miss            <= 1'b0; // cache is perfect here
            end

            // advance latency timers
            for (i = 0; i < 4; i = i + 1) begin
                if (state_q[i] == 1 && lat_q[i] != 0)
                    lat_q[i] <= lat_q[i] - 1;
                if (state_q[i] == 1 && lat_q[i] == 1)
                    state_q[i] <= 2;
            end

            // Commit in program order
            if (commit_ready) begin
                valid_q[head] <= 0;
                state_q[head] <= 0;
                lat_q[head]   <= 0;
                head          <= head + 1;
            end
        end
    end

    // simple dependency check function
    function [0:0] addr_match_before(input [1:0] idx);
        integer k;
        begin
            addr_match_before = 0;
            for (k = head; k != idx; k = k + 1) begin
                if (valid_q[k] && addr_q[k] == addr_q[idx] && state_q[k] != 2)
                    addr_match_before = 1;
            end
        end
    endfunction
endmodule
