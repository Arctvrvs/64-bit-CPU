# lsu Module

The `lsu.sv` file provides a simple two-port load/store unit used in early
pipeline simulations. It accepts up to two memory operations each cycle and
forwards them to the L1 data cache.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Asynchronous reset |
| `op_valid_i[2]` | in | 1 | Operation valid flags |
| `op_is_store_i[2]` | in | 1 | 1 for store, 0 for load |
| `op_addr_i[2]` | in | 64 | Address for the access |
| `op_store_data_i[2]` | in | 64 | Store data |
| `op_store_size_i[2]` | in | 3 | Store size encoding |
| `op_dest_phys_i[2]` | in | 7 | Destination physical register |
| `op_rob_idx_i[2]` | in | 8 | ROB index |
| `dc_req_valid_o[2]` | out | 1 | Request valid to data cache |
| `dc_req_addr_o[2]` | out | 64 | Address to data cache |
| `dc_req_wdata_o[2]` | out | 64 | Write data to cache |
| `dc_req_wstrb_o[2]` | out | 8 | Byte enables |
| `dc_req_is_write_o[2]` | out | 1 | Write enable to cache |
| `dc_rsp_ready_i[2]` | in | 1 | Cache response ready |
| `dc_rsp_rdata_i[2]` | in | 64 | Data returned by cache |
| `result_valid_o[2]` | out | 1 | Result valid for loads |
| `load_data_o[2]` | out | 64 | Load data |
| `dest_phys_o[2]` | out | 7 | Destination register |
| `rob_idx_o[2]` | out | 8 | ROB index |

## Behavior

For each valid operation the LSU now translates the virtual address through a
two-level TLB hierarchy implemented by `tlb_l1_64e_8w` and `tlb_l2_512e_8w`.
If neither TLB contains the mapping a request is sent to `page_walker8` and the
µop stalls until the walk completes. Translation faults are reported to the
caller. After a successful translation the unit issues a request to the data
cache. Loads return their data one cycle later assuming the cache responds
ready. Stores simply forward their data and do not produce a result. This
behavioral model still omits ordering rules but now mirrors the basic MMU
interaction expected in the RTL.

A lightweight Python `LSU` model mirrors this behavior for unit tests. It
uses the `DataMemoryModel` helper to service load and store operations.
When provided a `CoverageModel` instance the LSU records TLB hit/miss
statistics, lookup latency and permission faults. Page walks issued to its
`PageWalker8` helper are logged as well along with any resulting faults.
