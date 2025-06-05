# router_5port Module

`router_5port.sv` implements a simple five port router used in the 2×2 mesh interconnect. Each port represents a cardinal direction plus a local port.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Reset |
| `in_valid[4:0]` | in | 1 ea | Input packet valid flags |
| `in_packet[4:0][255:0]` | in | 256 ea | Packets from neighboring routers |
| `out_ready[4:0]` | in | 1 ea | Downstream ready signals |
| `out_valid[4:0]` | out | 1 ea | Output valid flags |
| `out_packet[4:0][255:0]` | out | 256 ea | Routed packets |

The placeholder simply forwards each input to the matching output when `out_ready` is high.
