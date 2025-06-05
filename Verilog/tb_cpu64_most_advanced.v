`timescale 1ns/1ps
// tb_cpu64_most_advanced.v
// Simple testbench for the wrapper around the out-of-order CPU.
module tb_cpu64_most_advanced;
    reg clk;
    reg rst_n;

    cpu64_most_advanced dut(
        .clk(clk),
        .rst_n(rst_n)
    );

    // Clock generation
    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        rst_n = 0;
        #20 rst_n = 1;
        #200 $finish;
    end
endmodule
