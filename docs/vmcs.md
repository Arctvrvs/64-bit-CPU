# vmcs Module

`vmcs.sv` provides a minimal virtualization control structure. It tracks
whether virtualization mode is active and records the current VM ID.
The stub offers `vm_on` and `vm_off` signals to switch modes and outputs
the active `current_vmid`.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `vm_on_i` | in | 1 | Enter virtualization |
| `vmid_i[7:0]` | in | 8 | VM identifier |
| `vm_off_i` | in | 1 | Exit virtualization |
| `current_vmid_o[7:0]` | out | 8 | Active VMID when running |
| `running_o` | out | 1 | High when virtualization active |
