# issue_queue_8wide Module

`issue_queue_8wide.sv` implements a small placeholder issue queue. Up to eight
micro‑operations can be dispatched to the queue each cycle and up to eight ready
operations are issued in order.  Each entry tracks a functional unit type and a
possible third operand used by floating‑point or vector instructions.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active‑low reset |
| `flush_i` | in | 1 | Clear all queued entries |
| `alloc_valid_i[7:0]` | in | 1 each | Dispatch valid flags |
| `func_type_i[7:0]` | in | 3 each | 0=int,1=fp,2=vector,3=mem,4=branch |
| `op1_i[7:0]` | in | 64 each | Operand 1 value (if ready) |
| `op2_i[7:0]` | in | 64 each | Operand 2 value (if ready) |
| `op3_i[7:0]` | in | 64 each | Operand 3 value (if ready) |
| `pred_mask_i[7:0]` | in | 64 each | Vector predicate mask |
| `src1_tag_i[7:0]` | in | 7 each | Source 1 physical reg |
| `src2_tag_i[7:0]` | in | 7 each | Source 2 physical reg |
| `src3_tag_i[7:0]` | in | 7 each | Source 3 physical reg |
| `dest_phys_i[7:0]` | in | 7 each | Destination physical reg |
| `rob_idx_i[7:0]` | in | 8 each | ROB index |
| `ready1_i[7:0]` | in | 1 each | Src1 ready |
| `ready2_i[7:0]` | in | 1 each | Src2 ready |
| `ready3_i[7:0]` | in | 1 each | Src3 ready |
| `wakeup_tag_i[7:0]` | in | 7 each | Broadcast dest tag |
| `wakeup_data_i[7:0]` | in | 64 each | Broadcast result value |
| `wakeup_valid_i[7:0]` | in | 1 each | Broadcast valid |
| `fu_int_free_i[1:0]` | in | 2 | Available int ALUs |
| `fu_mul_free_i` | in | 1 | Multiply/divide unit free |
| `fu_vec_free_i[1:0]` | in | 2 | Vector FMA pipelines free |
| `fu_mem_free_i[1:0]` | in | 2 | LSU pipelines free |
| `fu_branch_free_i` | in | 1 | Branch unit free |
| `iq_full_o` | out | 1 | Cannot accept eight new entries |
| `issue_valid_o[7:0]` | out | 1 each | Issued this cycle |
| `issue_op1_o[7:0]` | out | 64 each | Issued operand1 |
| `issue_op2_o[7:0]` | out | 64 each | Issued operand2 |
| `issue_op3_o[7:0]` | out | 64 each | Issued operand3 |
| `issue_pred_mask_o[7:0]` | out | 64 each | Issued predicate mask |
| `issue_dest_o[7:0]` | out | 7 each | Issued destination |
| `issue_rob_idx_o[7:0]` | out | 8 each | Issued ROB index |

The implementation still uses a single 128‑entry circular buffer for early
testing.  Entries are grouped by functional unit type so that the model can
respect which units are available each cycle. A simple wakeup bus updates
operand readiness whenever a matching destination tag is broadcast. Full
The `flush_i` input clears all entries, typically on a branch mispredict.
Full prioritization and bypass networks remain future work.
