// vector_unit.v
// Placeholder wide SIMD/vector unit (e.g., AVX-512/FMA).
module vector_unit(
    input  wire clk,
    input  wire rst_n,
    input  wire issue_ready,
    output wire commit_ready
);
    assign commit_ready = issue_ready;
endmodule
