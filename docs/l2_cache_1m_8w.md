# l2_cache_1m_8w Module

`l2_cache_1m_8w.sv` is a placeholder for the unified 1 MB 8‑way set associative
L2 cache. The current model simply acknowledges requests and returns zero data.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `req_valid_i` | in | 1 | Access valid |
| `req_addr_i` | in | 64 | Address |
| `req_write_i` | in | 1 | Write enable |
| `req_wdata_i` | in | 64 | Write data |
| `req_ready_o` | out | 1 | Always ready |
| `resp_rdata_o` | out | 64 | Read data (zero) |

This stub will later be expanded to include tags, replacement and connection to
lower memory.

A simple Python `L2Cache` helper in `rtl/cache/l2_cache.py` mimics the
behavior with a dictionary and is used by the unit tests.
