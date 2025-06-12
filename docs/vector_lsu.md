# vector_lsu Module

`vector_lsu.sv` provides a placeholder vector load/store unit. It issues up to
eight lane accesses per cycle.  The unit now supports simple gather/scatter
addressing where each lane address is `base_addr_i + index_i[j] * 2**scale_i`.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `valid_i` | in | 1 | Operation valid |
| `is_store_i` | in | 1 | 1 for store, 0 for load |
| `base_addr_i` | in | 64 | Base address for the vector |
| `index_i[7:0]` | in | 64 | Per-lane indices for gather/scatter |
| `scale_i` | in | 3 | Address scale (log2 of element size) |
| `store_data_i` | in | 512 | Data to store when `is_store_i` |
| `req_valid_o` | out | 1 | Request valid to data cache |
| `req_addr_o[7:0]` | out | 64 | Addresses for each lane |
| `req_wdata_o` | out | 512 | Store data forwarded to cache |
| `result_valid_o` | out | 1 | Load result valid |
| `load_data_o` | out | 512 | Loaded vector data |

## Behavior

When `valid_i` is asserted the module computes per-lane addresses
`base_addr_i + index_i[j] * 2**scale_i`.  Sequential operation is achieved by
providing `index_i[j]=j` and `scale_i=3` (for 8‑byte elements).  Store data is
forwarded unchanged and loads still return zero data in this stubbed SystemVerilog
version.  The Python :class:`VectorLSU` model performs the actual memory reads
and writes for unit tests.  The :class:`rtl.isa.golden_model.GoldenModel`
includes matching :py:meth:`gather` and :py:meth:`scatter` helpers used by the
scoreboard.
