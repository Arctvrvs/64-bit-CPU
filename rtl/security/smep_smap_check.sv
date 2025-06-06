// smep_smap_check.sv - SMEP/SMAP permission checker
//
// Purpose: raise a fault when supervisor accesses user pages without override
// according to SMEP (execute) and SMAP (data) settings.

module smep_smap_check(
    input  logic is_kernel_i,
    input  logic va_user_i,
    input  logic is_exec_i,
    input  logic smep_i,
    input  logic smap_i,
    input  logic override_i,
    output logic fault_o
);

    assign fault_o = (is_exec_i  & is_kernel_i & smep_i & va_user_i) |
                     (~is_exec_i & is_kernel_i & smap_i & va_user_i & ~override_i);

endmodule
