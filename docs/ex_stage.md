# ex_stage

`ex_stage` collects issued micro-ops from the issue queue and routes them
to the individual execution units. This placeholder implementation simply
performs an ADD for integer operations and produces results after a fixed
latency for other types.

## Interface

```
module ex_stage(
    input  logic       clk,
    input  logic       rst_n,
    input  logic [7:0] issue_valid,
    input  logic [63:0] op1 [7:0],
    input  logic [63:0] op2 [7:0],
    input  logic [6:0] dest_phys [7:0],
    input  logic [7:0] rob_idx [7:0],
    input  logic [3:0] fu_type [7:0],
    output logic [7:0] wb_valid,
    output logic [63:0] wb_data [7:0],
    output logic [6:0] wb_dest [7:0],
    output logic [7:0] wb_rob_idx [7:0]
);
```

The unit stores issued operations internally until their latency has
expired, at which point the result is broadcast on the writeback bus.
