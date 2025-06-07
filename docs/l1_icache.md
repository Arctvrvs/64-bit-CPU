# l1_icache_64k_8w Module

This document describes the `l1_icache_64k_8w.sv` module located in `rtl/cache`.
The cache stores instructions for the fetch pipeline and provides two read ports
to support 8-byte aligned instruction fetching.

## Parameters

| Name | Default | Description |
|------|---------|-------------|
| `LINE_BYTES` | 64 | Cache line size in bytes |
| `ASSOC` | 8 | Associativity |
| `SETS` | 128 | Number of sets |
| `OFFSET_BITS` | 6 | Byte offset width |
| `INDEX_BITS` | 7 | Set index width |
| `TAG_BITS` | 51 | Tag width |

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `req_valid_if1` | in | 1 | Request valid for port 1 |
| `req_addr_if1` | in | 64 | Address for port 1 |
| `req_valid_if2` | in | 1 | Request valid for port 2 |
| `req_addr_if2` | in | 64 | Address for port 2 |
| `ready_if1` | out | 1 | Data ready on port 1 |
| `data_if1` | out | 64 | Instruction data for port 1 |
| `ready_if2` | out | 1 | Data ready on port 2 |
| `data_if2` | out | 64 | Instruction data for port 2 |
| `miss_addr_if1` | out | 64 | Miss address forwarded to L2 (port 1) |
| `miss_addr_if2` | out | 64 | Miss address forwarded to L2 (port 2) |

## Behavior

The cache performs two tag and data lookups per cycle. On a miss the line is
allocated in an MSHR entry (up to eight entries). Replacement uses a 7-bit
pseudo-LRU per set. Before each lookup the virtual address is translated through
the instruction TLB hierarchy (`tlb_l1` → `tlb_l2` → `page_walker`).  Translation
misses or permission faults deassert the ready signal so the fetch stage stalls
until the page walker supplies a physical address. This module remains a
behavioral placeholder and does not implement full cache lookup logic yet.

A small Python helper `L1ICache` in `rtl/cache/l1_icache.py`
provides an in-memory model used by the unit tests. When supplied with a
`CoverageModel` instance the helper records L1 instruction cache hits and
misses.
