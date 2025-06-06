# vector_lsu Module

`vector_lsu.sv` provides a placeholder vector load/store unit. It issues up to eight lane accesses per cycle using sequential addresses derived from a base pointer.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `valid_i` | in | 1 | Operation valid |
| `is_store_i` | in | 1 | 1 for store, 0 for load |
| `base_addr_i` | in | 64 | Base address for the vector |
| `store_data_i` | in | 512 | Data to store when `is_store_i` |
| `req_valid_o` | out | 1 | Request valid to data cache |
| `req_addr_o[7:0]` | out | 64 | Addresses for each lane |
| `req_wdata_o` | out | 512 | Store data forwarded to cache |
| `result_valid_o` | out | 1 | Load result valid |
| `load_data_o` | out | 512 | Loaded vector data |

## Behavior

When `valid_i` is asserted the module produces eight sequential addresses starting at `base_addr_i` and forwards the store data if `is_store_i` is high. Loads return zero data in this stubbed version. The Python `VectorLSU` model performs the actual memory reads and writes for unit tests.
