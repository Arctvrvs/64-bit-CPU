# directory_mesi Module

`directory_mesi.sv` implements a small MESI directory for cache coherence. Each entry tracks the
state (`I`, `S`, or `M`) and a bitmask of sharer cores for one cache line. The directory
receives requests from L2 caches indicating the requesting core and whether the
access is a read or write.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `req_valid_i` | in | 1 | Request valid |
| `req_addr_i[63:0]` | in | 64 | Line address |
| `req_write_i` | in | 1 | 1 for write, 0 for read |
| `req_src_i[1:0]` | in | 2 | Requesting core ID |
| `resp_need_inval_o` | out | 1 | Other caches must invalidate |
| `resp_state_o[1:0]` | out | 2 | Current state encoding |

The stub simply updates an internal dictionary. For reads it marks the line as
Shared and adds the requester to the sharer mask. For writes it marks the line as
Modified by the requester and indicates whether any other sharers existed.
