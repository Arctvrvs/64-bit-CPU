# l3_cache_16m_8w Module

`l3_cache_16m_8w.sv` models a simple shared last level cache. It is a placeholder
for the final 16 MB 8‑way cache that will be connected via the mesh
interconnect. For now it responds in a single cycle using an associative
array.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `req_valid_i` | in | 1 | Access valid |
| `req_addr_i` | in | 64 | Address |
| `req_write_i` | in | 1 | Write enable |
| `req_wdata_i` | in | 64 | Write data |
| `resp_ready_i` | in | 1 | Response ready |
| `resp_valid_o` | out | 1 | Response valid |
| `resp_rdata_o` | out | 64 | Read data |

The SystemVerilog model stores 4096 doublewords in a small array and
always returns data the cycle after a request when `resp_ready_i` is
asserted.

A matching Python helper `L3Cache16M8W` located in
`rtl/interconnect/l3_cache_16m_8w.py` mirrors this behavior for unit
tests.
