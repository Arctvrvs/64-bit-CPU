// csr_unit.v
// Minimal CSR unit that maintains a handful of machine CSRs and a
// simplified privilege level. Real decoding of CSR instructions is
// omitted but the structure models state updates when issued.
module csr_unit(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        issue_valid,
    input  wire [2:0]  csr_op,     // 0=csrrw,1=csrrs,2=csrrc,3=csrrwi,4=csrrsi,5=csrrci
    input  wire [11:0] csr_addr,
    input  wire [63:0] write_data,
    output reg         commit_ready,
    output reg [63:0]  read_data,
    output reg [1:0]   priv_level,
    output reg         illegal_access
);
    reg [63:0] mstatus, mtvec, mepc, mie, mip, satp;
    reg [63:0] mtime, mtimecmp;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            commit_ready   <= 0;
            illegal_access <= 0;
            priv_level     <= 2'd3; // machine mode
            mstatus <= 0; mtvec <= 0; mepc <= 0;
            mie <= 0; mip <= 0; satp <= 0; read_data <= 0;
            mtime <= 0; mtimecmp <= 64'hffff_ffff_ffff_ffff;
        end else begin
            commit_ready   <= 0;
            illegal_access <= 0;
            mtime <= mtime + 64'd1;
            if (mtime >= mtimecmp)
                mip[7] <= 1; // set timer interrupt pending
            if (issue_valid) begin
                commit_ready <= 1;

                // default read
                case (csr_addr)
                    12'h300: read_data <= mstatus;
                    12'h304: read_data <= mie;
                    12'h305: read_data <= mtvec;
                    12'h341: read_data <= mepc;
                    12'h344: read_data <= mip;
                    12'h180: read_data <= satp;
                    12'hB00: read_data <= mtime;
                    12'hB01: read_data <= mtimecmp;
                    default: read_data <= 0;
                endcase

                // simple privilege check: only machine mode can access M CSRs
                if (csr_addr[9:8] == 2'b11 && priv_level != 2'd3)
                    illegal_access <= 1;
                else begin
                    case (csr_op)
                        3'd0: csr_write(csr_addr, write_data); // CSRRW
                        3'd1: csr_set(csr_addr, write_data);   // CSRRS
                        3'd2: csr_clear(csr_addr, write_data); // CSRRC
                        3'd3: csr_write(csr_addr, {59'b0, csr_addr[4:0]}); // CSRRWI
                        3'd4: csr_set  (csr_addr, {59'b0, csr_addr[4:0]}); // CSRRSI
                        3'd5: csr_clear(csr_addr, {59'b0, csr_addr[4:0]}); // CSRRCI
                    endcase
                end

                // update privilege level from mstatus bits
                priv_level <= mstatus[12:11];
                if (csr_addr == 12'hB01) begin
                    mtimecmp <= write_data;
                    mip[7] <= 0; // clear pending timer interrupt
                end
            end
        end
    end

    task csr_write(input [11:0] addr, input [63:0] data);
        begin
            case (addr)
                12'h300: mstatus <= data;
                12'h304: mie     <= data;
                12'h305: mtvec   <= data;
                12'h341: mepc    <= data;
                12'h344: mip     <= data;
                12'h180: satp    <= data;
                12'hB00: mtime   <= data;
                12'hB01: mtimecmp<= data;
            endcase
        end
    endtask

    task csr_set(input [11:0] addr, input [63:0] data);
        begin
            case (addr)
                12'h300: mstatus <= mstatus | data;
                12'h304: mie     <= mie | data;
                12'h305: mtvec   <= mtvec | data;
                12'h341: mepc    <= mepc | data;
                12'h344: mip     <= mip | data;
                12'h180: satp    <= satp | data;
                12'hB00: mtime   <= mtime | data;
                12'hB01: mtimecmp<= mtimecmp | data;
            endcase
        end
    endtask

    task csr_clear(input [11:0] addr, input [63:0] data);
        begin
            case (addr)
                12'h300: mstatus <= mstatus & ~data;
                12'h304: mie     <= mie & ~data;
                12'h305: mtvec   <= mtvec & ~data;
                12'h341: mepc    <= mepc & ~data;
                12'h344: mip     <= mip & ~data;
                12'h180: satp    <= satp & ~data;
                12'hB00: mtime   <= mtime & ~data;
                12'hB01: mtimecmp<= mtimecmp & ~data;
            endcase
        end
    endtask
endmodule
