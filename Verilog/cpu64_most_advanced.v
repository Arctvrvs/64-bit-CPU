`timescale 1ns/1ps
// cpu64_most_advanced.v
// Wrapper module that instantiates the experimental out-of-order CPU.
module cpu64_most_advanced(
    input  wire clk,
    input  wire rst_n
);
    cpu64_outoforder cpu_u(
        .clk   (clk),
        .rst_n (rst_n)
    );
endmodule
