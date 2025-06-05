// hazard_unit.v
module hazard_unit (
    input  wire       idex_mem_read,   // 1 if ID/EX stage is a load
    input  wire [4:0] idex_rd,         // register being loaded in ID/EX
    input  wire [4:0] ifid_rs1,        // rs1 of instruction in IF/ID
    input  wire [4:0] ifid_rs2,        // rs2 of instruction in IF/ID
    output reg        stall            // 1 => stall the pipeline
);
    always @(*) begin
        if ((idex_mem_read) && 
            ((idex_rd == ifid_rs1) || (idex_rd == ifid_rs2))) begin
            stall = 1'b1;
        end else begin
            stall = 1'b0;
        end
    end
endmodule
