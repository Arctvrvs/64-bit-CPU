# page_walker Module

`page_walker.sv` models a very small page table walker used when both the L1 and
L2 TLB miss. It contains an internal table of up to 16 entries and performs a
simple associative lookup.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `req_valid_i` | in | 1 | Translation request valid |
| `req_vaddr_i` | in | 64 | Virtual address |
| `req_perm_i` | in | 3 | Permission bits |
| `resp_valid_o` | out | 1 | Response valid |
| `resp_paddr_o` | out | 64 | Physical address |
| `fault_o` | out | 1 | Permission fault |

## Behavior

The walker searches its table for the requested virtual address. If found it
returns the physical address and fault status according to the stored
permission bits. This placeholder does not implement page table walks from
memory.
