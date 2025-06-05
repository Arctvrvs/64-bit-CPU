# tlb_l1_64e_8w Module

`tlb_l1_64e_8w.sv` implements a small fully associative Level&nbsp;1
Translation Lookaside Buffer. It is shared by the instruction fetch path
and the load/store unit.

## Parameters

| Name | Default | Description |
|------|---------|-------------|
| `ENTRIES` | 64 | Number of TLB entries |

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `lookup_valid` | in | 1 | Perform a TLB lookup |
| `va_i` | in | 64 | Virtual address |
| `perm_req_i` | in | 3 | Access type `{R,W,X}` |
| `hit_o` | out | 1 | Hit flag |
| `pa_o` | out | 64 | Physical address when hit |
| `perm_fault_o` | out | 1 | Permission fault detected |
| `refill_valid` | in | 1 | Insert new entry |
| `refill_va_i` | in | 64 | Virtual address for refill |
| `refill_pa_i` | in | 64 | Physical address for refill |
| `refill_perm_i` | in | 3 | Permission bits for entry |

## Behavior

The TLB performs an associative lookup each cycle. When `refill_valid` is
asserted a new entry overwrites the first slot. Permission bits are checked
during lookup; if the requested access is not allowed `perm_fault_o` is set.
This model does not implement replacement or ASID tagging and is intended
only for early bring-up.
