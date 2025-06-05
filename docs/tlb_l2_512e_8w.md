# tlb_l2_512e_8w Module

This file documents the placeholder level‑2 TLB with 512 entries. The module
accepts a virtual address and permission bits and returns the translated physical
address if present.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Asynchronous reset |
| `req_valid_i` | in | 1 | Translation request valid |
| `req_vaddr_i` | in | 64 | Virtual address |
| `req_perm_i` | in | 3 | Permission bits |
| `hit_o` | out | 1 | Hit flag |
| `resp_paddr_o` | out | 64 | Physical address |
| `fault_o` | out | 1 | Permission fault |
| `refill_valid_i` | in | 1 | Refill entry |
| `refill_vaddr_i` | in | 64 | Virtual address to insert |
| `refill_paddr_i` | in | 64 | Physical address |
| `refill_perm_i` | in | 3 | Permissions |

## Behavior

Entries are indexed by bits [8:0] of the virtual address. On a refill the
selected entry is overwritten. During lookup if the stored virtual address
matches, the physical address is returned and `hit_o` asserted.
