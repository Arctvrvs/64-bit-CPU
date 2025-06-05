# ept Module

`ept.sv` is a placeholder Extended Page Table translator. For each
translation request it XORs the guest physical address with a per-VM key
and returns the resulting host physical address. No actual page table
walks are performed.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `translate_valid_i` | in | 1 | Request valid |
| `vmid_i[7:0]` | in | 8 | VM identifier |
| `gpa_i[63:0]` | in | 64 | Guest physical address |
| `hpa_o[63:0]` | out | 64 | Host physical address |
| `fault_o` | out | 1 | Always zero in the stub |
