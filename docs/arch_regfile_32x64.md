# arch_regfile_32x64 Module

The `arch_regfile_32x64.sv` module implements the architectural register file
(ARF) used by the decode and rename stages. It provides a single synchronous
write port and three asynchronous read ports for the thirty-two 64‑bit
registers defined by the RV64 ISA.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `we0` | in | 1 | Write enable for the single write port |
| `waddr0[4:0]` | in | 5 | Register index to write |
| `wdata0[63:0]` | in | 64 | Data to write |
| `raddr0[4:0]` | in | 5 | Read address port 0 |
| `rdata0[63:0]` | out | 64 | Data from port 0 |
| `raddr1[4:0]` | in | 5 | Read address port 1 |
| `rdata1[63:0]` | out | 64 | Data from port 1 |
| `raddr2[4:0]` | in | 5 | Read address port 2 |
| `rdata2[63:0]` | out | 64 | Data from port 2 |

## Behavior

Values written on the rising edge of `clk` appear on the selected register the
following cycle when `we0` is asserted. Read ports are purely combinational so
that the current value of a register is available without waiting for a clock
edge.
