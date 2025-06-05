# sgx_enclave Module

`sgx_enclave.sv` is a lightweight placeholder implementing basic Intel SGX-like enclave control. It keeps track of enclave pages and exposes minimal commands to enter and exit enclave mode.

## Commands

The module supports the following one-hot command inputs:

| Signal | Description |
|-------|-------------|
| `ecreate_i` | Reserve a page in the EPC memory map |
| `eadd_i` | Add the page at `addr_i` with data `wdata_i` |
| `einit_i` | Finalise the enclave and record the measurement |
| `eenter_i` | Enter enclave mode; only EPC pages are accessible |
| `eexit_i` | Leave enclave mode |

Additional inputs `addr_i[63:0]` and `wdata_i[63:0]` provide the page address and data for `EADD`. When in enclave mode `access_addr_i[63:0]` can be checked. If the address is not part of the EPC, `sgx_fault_o` is asserted.

## Outputs

| Signal | Width | Description |
|------|-------|-------------|
| `active_o` | 1 | High when executing inside the enclave |
| `sgx_fault_o` | 1 | Indicates an out-of-enclave access while active |

The implementation is highly simplified but suffices to model enclave entry and permission checks for early verification.
