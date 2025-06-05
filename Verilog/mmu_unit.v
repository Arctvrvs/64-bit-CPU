// mmu_unit.v
// Simplified MMU that translates virtual addresses using a fixed
// page table base register.  A tiny four entry TLB caches recent
// translations.
module mmu_unit(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [63:0] virt_addr,
    input  wire        access_write,
    output reg  [63:0] phys_addr,
    output reg         fault
);
    reg [63:0] satp; // page table base pointer
    reg [51:0] tlb_vpn [0:7];
    reg [51:0] tlb_ppn [0:7];
    reg [2:0]  tlb_perm[0:7]; // r,w,x
    reg        tlb_valid[0:7];
    reg  [2:0] lru [0:7];
    integer i;
    reg [2:0]  replace_ptr;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            satp <= 64'h8000_0000; // dummy base
            phys_addr <= 0;
            fault <= 0;
            replace_ptr <= 0;
            for (i = 0; i < 8; i = i + 1) begin
                tlb_valid[i] <= 0;
                tlb_vpn[i]   <= 0;
                tlb_ppn[i]   <= 0;
                tlb_perm[i]  <= 3'b111; // allow all
                lru[i]       <= i;
            end
        end else begin
            fault <= 0;
            // lookup TLB (simple fully-associative with round-robin replace)
            integer hit;
            hit = -1;
            for (i = 0; i < 8; i = i + 1) begin
                if (tlb_valid[i] && tlb_vpn[i] == virt_addr[63:12])
                    hit = i;
            end

            if (hit >= 0) begin
                if (access_write && !tlb_perm[hit][1]) begin
                    fault <= 1; // write not allowed
                end else begin
                    phys_addr <= {tlb_ppn[hit], virt_addr[11:0]};
                end
                lru[hit] <= replace_ptr; // update LRU tag
            end else begin
                // miss - create simple translation and insert
                tlb_vpn[replace_ptr]  <= virt_addr[63:12];
                tlb_ppn[replace_ptr]  <= satp[63:12] + virt_addr[63:12];
                tlb_perm[replace_ptr] <= 3'b111;
                tlb_valid[replace_ptr] <= 1;
                lru[replace_ptr] <= replace_ptr;
                phys_addr <= {satp[63:12] + virt_addr[63:12], virt_addr[11:0]};
                replace_ptr <= replace_ptr + 1;
            end
        end
    end
endmodule
