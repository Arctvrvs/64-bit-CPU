// spec_fetch_fence.sv - Speculative fetch fence unit
//
// Purpose: Blocks loads until earlier branches retire. This simple
// placeholder keeps a count of pending fences and deasserts
// allow_load_o when any are outstanding.

module spec_fetch_fence(
    input  logic clk,
    input  logic rst_n,
    input  logic fence_i,
    input  logic retire_branch_i,
    output logic allow_load_o
);
    int pending;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pending <= 0;
        end else begin
            if (fence_i)
                pending <= pending + 1;
            if (retire_branch_i && pending > 0)
                pending <= pending - 1;
        end
    end

    assign allow_load_o = (pending == 0);
endmodule
