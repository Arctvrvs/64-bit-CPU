# if_buffer_16 Module

`if_buffer_16.sv` implements a simple FIFO used between the instruction cache and
decoder. It can store up to 16 instructions (128 bytes) and outputs two
instructions (64 bits) per cycle.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `enq_valid` | in | 1 | Instruction available to enqueue |
| `enq_data` | in | 64 | Two concatenated instructions |
| `enq_ready` | out | 1 | Buffer can accept data |
| `deq_ready` | in | 1 | Downstream stage ready |
| `deq_valid` | out | 1 | Data available to dequeue |
| `deq_data` | out | 64 | Two instructions read from buffer |

The current implementation is a behavioral placeholder and does not model
stall or flush signals.
