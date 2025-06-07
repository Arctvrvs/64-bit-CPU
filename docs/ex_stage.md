# ex_stage

`ex_stage` collects issued micro-ops from the issue queue and routes them
to the individual execution units. The early implementation performs very
basic arithmetic: integer operations are simple adds, multiply/divide
operations return a product after three cycles, vector operations perform a
fused multiply-add on a third operand, memory operations return their second
operand after two cycles and branch operations resolve in a single cycle.

## Interface

```
module ex_stage(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       flush_i,
    input  logic [7:0] issue_valid,
    input  logic [63:0] op1 [7:0],
    input  logic [63:0] op2 [7:0],
    input  logic [63:0] op3 [7:0],
    input  logic [63:0] pc [7:0],
    input  logic [2:0] branch_ctrl [7:0],
    input  logic [6:0] dest_phys [7:0],
    input  logic [7:0] rob_idx [7:0],
    input  logic [3:0] fu_type [7:0],
    input  logic [7:0] pred_taken,
    input  logic [63:0] pred_target [7:0],
    output logic [1:0] fu_int_free_o,
    output logic       fu_mul_free_o,
    output logic [1:0] fu_vec_free_o,
    output logic [1:0] fu_mem_free_o,
    output logic       fu_branch_free_o,
    output logic [7:0] br_mispredict,
    output logic [63:0] br_target [7:0],
    output logic [7:0] wb_valid,
    output logic [63:0] wb_data [7:0],
    output logic [6:0] wb_dest [7:0],
    output logic [7:0] wb_rob_idx [7:0]
);
```

`flush_i` clears any queued operations in the stage. The unit stores issued
operations internally until their latency has expired, at which point the
result is broadcast on the writeback bus.

Branch operations are resolved through the `branch_unit` helper.  Each issued
branch supplies its program counter, branch control field, predicted taken flag
and predicted target.  The actual outcome and target are compared against the
prediction so `br_mispredict` and `br_target` report mispredictions accurately.

The stage also exposes the availability of its functional units so that the
issue queue knows how many operations can be dispatched each cycle.  The
`fu_*_free_o` signals report the number of free integer ALU pipelines,
availability of the multiply/divide unit, the two vector FMA pipelines, the two
LSU request ports and the branch unit.
