# l1_dcache_64k_8w Module

`l1_dcache_64k_8w.sv` implements a placeholder 64&nbsp;KB 8-way set associative
data cache. Each request address is first translated through a small two-level
TLB hierarchy consisting of `tlb_l1_64e_8w`, `tlb_l2_512e_8w` and a
`page_walker8` model. The resulting physical address indexes the internal
memory array. Permission faults or translation misses deassert the ready signal
so the LSU stalls until translation completes. Tag checking and miss handling
of the cache itself are left for future refinement.

## Parameters

| Name | Default | Description |
|------|---------|-------------|
| `LINE_BYTES` | 64 | Cache line size in bytes |
| `ASSOC` | 8 | Associativity |
| `SETS` | 128 | Number of sets |

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `req_valid_i[2]` | in | 1 | Request valid per port |
| `req_addr_i[2]` | in | 64 | Byte address |
| `req_wdata_i[2]` | in | 64 | Write data |
| `req_wstrb_i[2]` | in | 8 | Byte write strobes |
| `req_is_write_i[2]` | in | 1 | Write enable |
| `rsp_ready_o[2]` | out | 1 | Response ready |
| `rsp_rdata_o[2]` | out | 64 | Read data |

## Behavior

Each access is performed against a backing array representing 64&nbsp;KB of
memory. Writes update bytes according to the strobe mask. Reads return the
stored value. All operations appear to complete in one cycle with no stalls,
which is sufficient for initial bring-up.
\nA small Python helper `L1DCache` in `rtl/cache/l1_dcache.py`\nprovides an in-memory model used by unit tests. When given a
`CoverageModel` instance it logs cache hits and misses for the L1 level.
