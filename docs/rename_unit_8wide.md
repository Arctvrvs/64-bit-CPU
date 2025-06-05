# rename_unit_8wide Module

`rename_unit_8wide.sv` provides a simple register renaming implementation for
up to eight decoded instructions each cycle. It maps architectural register
indices to physical register indices using an internal rename table and free
list.

## Function

- Maintains a mapping `arch_to_phys[31:0]`.
- Allocates physical registers from a free list initially containing indices
  32 through 127.
- For each valid instruction, outputs the physical source registers and a newly
  allocated destination register along with the previous mapping (`old_rd_phys`).
- Allocation occurs only when the ROB and reservation stations can accept eight
  new entries and at least eight free physical registers are available.

This first version does not implement branch checkpointing or recovery.

## I/O Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `clk` | in | 1 | Clock |
| `rst_n` | in | 1 | Active-low reset |
| `valid_in[7:0]` | in | 1 each | Instruction valid flags |
| `rs1_arch_i[7:0]` | in | 5 each | Source register 1 |
| `rs2_arch_i[7:0]` | in | 5 each | Source register 2 |
| `rd_arch_i[7:0]` | in | 5 each | Destination register |
| `can_allocate_rob8` | in | 1 | ROB has room for 8 entries |
| `can_allocate_rs8` | in | 1 | Issue queue has room |
| `rs1_phys_o[7:0]` | out | 7 each | Physical source 1 |
| `rs2_phys_o[7:0]` | out | 7 each | Physical source 2 |
| `rd_phys_o[7:0]` | out | 7 each | Allocated destination |
| `old_rd_phys_o[7:0]` | out | 7 each | Previous mapping of destination |
| `rename_valid_o[7:0]` | out | 1 each | Allocation successful |
| `free_list_count_o` | out | 7 | Remaining free registers |

`rename_unit_8wide` is a behavioral placeholder and will be extended with
branch checkpointing and recovery logic.

