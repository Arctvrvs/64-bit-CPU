# page_walker8 Module

`page_walker8.sv` implements a simplified page table walker able to service up to
8 concurrent translation requests. Each request specifies the virtual address and
required permissions. The module contains a small associative array of 16
entries and produces a physical address with a fault flag in a single cycle.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `walk_valid_i[7:0]` | in | 1 each | Request valid per entry |
| `walk_vaddr_i[8][63:0]` | in | 64 | Virtual addresses |
| `walk_perm_i[8][2:0]` | in | 3 | Required permission bits |
| `walk_ready_o[7:0]` | out | 1 each | Walker ready per entry |
| `resp_valid_o[7:0]` | out | 1 each | Response valid per entry |
| `resp_paddr_o[8][63:0]` | out | 64 | Translated physical addresses |
| `resp_fault_o[7:0]` | out | 1 each | Permission fault per entry |

## Behavior

Whenever a request is valid the walker checks its internal table for the
matching virtual address. If found it returns the physical address and sets the
fault flag when the requested permissions are not allowed. This model completes
in one cycle and is intended for unit tests.

A small Python model `PageWalker8` in `rtl/mmu/page_walker8.py` mirrors the
SystemVerilog behavior for use in tests.
