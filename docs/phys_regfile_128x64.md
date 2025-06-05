# phys_regfile_128x64 Module

The `phys_regfile_128x64.sv` module implements the physical register file used by the rename and issue stages. It stores 128 64‑bit registers and provides four synchronous write ports and six asynchronous read ports to sustain the throughput of an 8‑wide out‑of‑order pipeline.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `we0` | in | 1 | Write enable port 0 |
| `waddr0[6:0]` | in | 7 | Write address port 0 |
| `wdata0[63:0]` | in | 64 | Data for port 0 |
| `we1` | in | 1 | Write enable port 1 |
| `waddr1[6:0]` | in | 7 | Write address port 1 |
| `wdata1[63:0]` | in | 64 | Data for port 1 |
| `we2` | in | 1 | Write enable port 2 |
| `waddr2[6:0]` | in | 7 | Write address port 2 |
| `wdata2[63:0]` | in | 64 | Data for port 2 |
| `we3` | in | 1 | Write enable port 3 |
| `waddr3[6:0]` | in | 7 | Write address port 3 |
| `wdata3[63:0]` | in | 64 | Data for port 3 |
| `raddr0[6:0]` | in | 7 | Read address port 0 |
| `rdata0[63:0]` | out | 64 | Data from port 0 |
| `raddr1[6:0]` | in | 7 | Read address port 1 |
| `rdata1[63:0]` | out | 64 | Data from port 1 |
| `raddr2[6:0]` | in | 7 | Read address port 2 |
| `rdata2[63:0]` | out | 64 | Data from port 2 |
| `raddr3[6:0]` | in | 7 | Read address port 3 |
| `rdata3[63:0]` | out | 64 | Data from port 3 |
| `raddr4[6:0]` | in | 7 | Read address port 4 |
| `rdata4[63:0]` | out | 64 | Data from port 4 |
| `raddr5[6:0]` | in | 7 | Read address port 5 |
| `rdata5[63:0]` | out | 64 | Data from port 5 |

## Behavior

Values written on the rising edge of `clk` appear in the register file the next cycle when the corresponding `weX` is asserted. All read ports are purely combinational to deliver register contents for issue without additional latency.
