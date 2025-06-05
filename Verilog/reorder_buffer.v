// reorder_buffer.v
// Small reorder buffer that tracks in-flight instructions and commits
// them in program order once execution is complete.  Additional entries
// have been added and each slot now models a tiny execution latency.
module reorder_buffer(
    input  wire clk,
    input  wire rst_n,
    input  wire issue_ready,
    output reg  commit_ready
);
    reg        valid_q[0:31];
    reg [1:0]  state_q [0:31]; // 0=free 1=exec 2=done
    reg [2:0]  lat_q   [0:31];
    reg [5:0]  head, tail;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            head <= 0; tail <= 0;
            commit_ready <= 0;
            for (i = 0; i < 32; i = i + 1) begin
                valid_q[i] <= 0; state_q[i] <= 0; lat_q[i] <= 0;
            end
        end else begin
            commit_ready <= 0;

            // allocate entry
            if (issue_ready && !valid_q[tail]) begin
                valid_q[tail] <= 1;
                state_q[tail] <= 1; // executing
                lat_q[tail]   <= {$random} % 3 + 1;
                tail <= tail + 1;
            end

            // advance execution state
            for (i = 0; i < 32; i = i + 1) begin
                if (valid_q[i] && state_q[i] == 1 && lat_q[i] != 0)
                    lat_q[i] <= lat_q[i] - 1;
                if (valid_q[i] && state_q[i] == 1 && lat_q[i] == 1)
                    state_q[i] <= 2;
            end

            // commit if done
            if (valid_q[head] && state_q[head] == 2) begin
                commit_ready  <= 1;
                valid_q[head] <= 0;
                state_q[head] <= 0;
                lat_q[head]   <= 0;
                head <= head + 1;
            end
        end
    end
endmodule
