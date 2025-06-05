# csr_file Module

`csr_file.sv` implements a tiny control and status register block used for
initial bring‑up. It stores a handful of writable CSRs and tracks the `cycle`
and `instret` counters.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `raddr_i[11:0]` | in | 12 | Address of CSR to read |
| `rdata_o[63:0]` | out | 64 | CSR read data |
| `waddr_i[11:0]` | in | 12 | Address of CSR to write |
| `wdata_i[63:0]` | in | 64 | Data for CSR write |
| `we_i` | in | 1 | Write enable |
| `instret_inc_i[63:0]` | in | 64 | Increment for the instret counter |

`cycle` at address `0xC00` increments every cycle. `instret` at address `0xC02`
increments by `instret_inc_i` each cycle. A small array of 32 additional CSRs
is provided for software to read and write.
