# smep_smap_check Module

`smep_smap_check.sv` combines SMEP and SMAP permission checks. It raises a fault when the supervisor attempts to execute or access a user page without override according to the SMEP/SMAP configuration bits.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `is_kernel_i` | in | 1 | Current privilege level (1 if supervisor) |
| `va_user_i` | in | 1 | Indicates the page is user mode |
| `is_exec_i` | in | 1 | 1 for instruction fetch/execute |
| `smep_i` | in | 1 | SMEP enable flag |
| `smap_i` | in | 1 | SMAP enable flag |
| `override_i` | in | 1 | SMAP override for string ops |
| `fault_o` | out | 1 | Asserted when access is not allowed |

## Behavior

The checker reports a fault if:

* Instruction fetch while in supervisor mode accesses a user page and `smep_i` is set.
* A data access in supervisor mode targets a user page while `smap_i` is set and `override_i` is low.
