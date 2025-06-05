# l1_dcache_64k_8w Module

`l1_dcache_64k_8w.sv` implements a placeholder 64&nbsp;KB 8-way set associative
data cache. The current model simply stores 64&nbsp;KB of memory and completes
all read and write operations in a single cycle. Tag checking and miss handling
are left for future refinement.

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
