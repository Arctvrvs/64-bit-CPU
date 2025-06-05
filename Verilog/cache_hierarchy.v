// cache_hierarchy.v
// Very small direct-mapped cache used to model a cache hierarchy.  A tiny
// two-level cache now exists so that the performance counter can observe
// simple cache misses.
module cache_hierarchy(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        mem_read,
    input  wire        mem_write,
    input  wire [63:0] addr,
    input  wire [63:0] write_data,
    output reg  [63:0] read_data,
    output reg         miss
);
    // 2-way set associative L1
    reg [63:0] l1_data[0:3];
    reg [59:0] l1_tag [0:3];
    reg        l1_valid[0:3];
    reg        l1_lru  [0:1];
    reg [63:0] l2_data[0:7];
    reg [59:0] l2_tag [0:7];
    reg        l2_valid[0:7];
    wire [1:0] set_index = addr[3:2];
    wire [2:0] l2_index  = addr[4:2];
    wire [59:0] tag_in = addr[63:4];

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 4; i = i + 1) begin
                l1_valid[i] <= 0; l1_data[i]  <= 0; l1_tag[i]   <= 0;
            end
            l1_lru[0] <= 0; l1_lru[1] <= 0;
            for (i = 0; i < 8; i = i + 1) begin
                l2_valid[i] <= 0; l2_data[i] <= 0; l2_tag[i] <= 0;
            end
            read_data <= 0; miss <= 0;
        end else begin
            integer w0, w1, use;
            w0 = {set_index,1'b0};
            w1 = {set_index,1'b1};

            if (mem_write) begin
                use = l1_lru[set_index] ? w0 : w1;
                l1_data[use]  <= write_data;
                l1_tag[use]   <= tag_in;
                l1_valid[use] <= 1;
                l1_lru[set_index] <= ~l1_lru[set_index];
            end

            miss <= 0;
            if (mem_read) begin
                if (l1_valid[w0] && l1_tag[w0] == tag_in) begin
                    read_data <= l1_data[w0];
                    l1_lru[set_index] <= 1'b1; // way1 is next victim
                end else if (l1_valid[w1] && l1_tag[w1] == tag_in) begin
                    read_data <= l1_data[w1];
                    l1_lru[set_index] <= 1'b0; // way0 is next victim
                end else if (l2_valid[l2_index] && l2_tag[l2_index] == tag_in) begin
                    read_data <= l2_data[l2_index];
                    use = l1_lru[set_index] ? w0 : w1;
                    l1_data[use]  <= l2_data[l2_index];
                    l1_tag[use]   <= l2_tag[l2_index];
                    l1_valid[use] <= 1;
                    l1_lru[set_index] <= ~l1_lru[set_index];
                end else begin
                    read_data <= 64'b0;
                    miss <= 1;
                end
            end
        end
    end
endmodule
