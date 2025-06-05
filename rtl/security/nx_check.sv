// nx_check.sv - No-Execute permission checker
//
// Purpose: Raises a fault when instruction fetch occurs to a page marked
// non-executable. Simple combinational logic with one-cycle latency.

module nx_check(
    input  logic fetch_valid_i,
    input  logic nx_flag_i,
    output logic fault_o
);

    assign fault_o = fetch_valid_i & nx_flag_i;

endmodule
