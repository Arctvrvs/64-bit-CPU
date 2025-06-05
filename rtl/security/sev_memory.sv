// sev_memory.sv - SEV memory encryption stub
//
// Purpose: XORs read and write data with a per-VM key. Used to model AMD
// SEV style memory encryption for early testing.

module sev_memory (
    input  logic [63:0] key_i,
    input  logic [63:0] data_in_i,
    output logic [63:0] enc_data_o,
    input  logic [63:0] data_enc_i,
    output logic [63:0] dec_data_o
);

    assign enc_data_o = data_in_i ^ key_i;
    assign dec_data_o = data_enc_i ^ key_i;

endmodule
