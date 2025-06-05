# issue_queue_8wide Module

`issue_queue_8wide.sv` implements a very small placeholder issue queue. Up to
 eight micro‑operations can be dispatched to the queue each cycle and up to two
 ready operations are issued in order.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `alloc_valid_i[7:0]` | in | 1 each | Dispatch valid flags |
| `op1_i[7:0]` | in | 64 each | Operand 1 value |
| `op2_i[7:0]` | in | 64 each | Operand 2 value |
| `dest_phys_i[7:0]` | in | 7 each | Destination physical reg |
| `rob_idx_i[7:0]` | in | 8 each | ROB index |
| `ready1_i[7:0]` | in | 1 each | Src1 ready |
| `ready2_i[7:0]` | in | 1 each | Src2 ready |
| `iq_full_o` | out | 1 | Cannot accept eight new entries |
| `issue_valid_o[1:0]` | out | 1 each | Issued this cycle |
| `issue_op1_o[1:0]` | out | 64 each | Issued operand1 |
| `issue_op2_o[1:0]` | out | 64 each | Issued operand2 |
| `issue_dest_o[1:0]` | out | 7 each | Issued destination |
| `issue_rob_idx_o[1:0]` | out | 8 each | Issued ROB index |

The implementation uses a small 16‑entry circular buffer and does not model
wakeup broadcasts or prioritization. It is only intended for early testing.
