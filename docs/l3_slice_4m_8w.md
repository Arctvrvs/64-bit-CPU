# l3_slice_4m_8w Module

`l3_slice_4m_8w.sv` models a single 4 MB slice of the shared L3 cache. In the final design four slices form the 16 MB last level cache.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `req_valid_i` | in | 1 | Access request valid |
| `req_addr_i[63:0]` | in | 64 | Address |
| `req_write_i` | in | 1 | Write enable |
| `req_wdata_i[63:0]` | in | 64 | Write data |
| `resp_ready_i` | in | 1 | Response ready |
| `resp_valid_o` | out | 1 | Response valid |
| `resp_rdata_o[63:0]` | out | 64 | Read data |

The current stub simply stores data in a dictionary keyed by address.
