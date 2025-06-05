# nx_check Module

The `nx_check` module implements a simple no-execute permission check used during
instruction fetch. Given a valid fetch request and a flag from the page table
entry indicating that execution is disallowed, the module outputs a fault signal.
It is intended as a lightweight security feature.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `fetch_valid_i` | in | 1 | Fetch request valid |
| `nx_flag_i` | in | 1 | NX bit from the TLB/page table |
| `fault_o` | out | 1 | Asserted when execution is not allowed |

## Behavior

Whenever a fetch is attempted (`fetch_valid_i` high) and the NX flag is set,
`fault_o` is asserted. Otherwise the output remains low.
