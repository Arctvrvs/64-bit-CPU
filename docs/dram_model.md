# dram_model Module

`dram_model.sv` provides a very small memory model for simulation. The current version is purely behavioral and stores 64-bit words in a dictionary.

## Interface

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `req_valid` | in | 1 | Request valid |
| `req_write` | in | 1 | Write enable |
| `req_addr[63:0]` | in | 64 | Address |
| `req_wdata[63:0]` | in | 64 | Write data |
| `resp_ready` | in | 1 | Ready to accept read data |
| `resp_valid` | out | 1 | Response valid |
| `resp_rdata[63:0]` | out | 64 | Read data |

Reads and writes complete in a single cycle in this placeholder.

A Python implementation `DRAMModel` in `rtl/interconnect/dram_model.py`
offers equivalent behavior for the unit tests.
