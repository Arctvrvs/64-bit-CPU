# Simple Makefile to build the advanced CPU testbench

VERILOG_FILES=$(wildcard Verilog/*.v)

default: run

cpu64_tb: $(VERILOG_FILES)
	iverilog -o cpu64_tb $(VERILOG_FILES)

run: cpu64_tb
	vvp cpu64_tb

clean:
	rm -f cpu64_tb
