# smt_arbitration

A simple two-thread round-robin scheduler used to multiplex shared CPU
resources when simultaneous multithreading is enabled. Each cycle the
module grants at most one thread access when both request the same
resource.

```
module smt_arbitration(
    input  logic clk,
    input  logic rst_n,
    input  logic t0_req,
    input  logic t1_req,
    output logic grant_t0,
    output logic grant_t1
);
```
