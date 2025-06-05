# Golden Model

The `golden_model.py` file located under `rtl/isa` provides a tiny reference
implementation of a 64‑bit RISC‑V interpreter. It is not cycle accurate but
implements a minimal subset of RV64I so that UVM testbenches can compare
results against expected behavior.

Currently supported instructions include:

- Integer ALU operations (`ADD`, `SUB`, `AND`, `OR`, `XOR`,
  `SLL`, `SRL`, `SRA`, `ADDI`, `ANDI`, `ORI`, `XORI`,
  `SLLI`, `SRLI`, `SRAI`, `LUI`, `AUIPC`)
- Load/store (`LW`/`LD`, `SW`/`SD` simplified as 64‑bit accesses)
- Integer ALU operations (`ADD`, `SUB`, `ADDI`)
- Load/store (`LW`, `SW` simplified as 64‑bit accesses)
- Branches (`BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`)
- Jumps (`JAL`, `JALR`)
- Multiply/divide (`MUL`, `DIV`, `REM` and variants)
- Basic atomic operations (`LR.D`, `SC.D`, `AMOADD.D`, `AMOSWAP.D`)

The `GoldenModel` class maintains an array of 32 general purpose registers,
a dictionary based memory and the current program counter. The `step` method
decodes and executes a single 32‑bit instruction. The helper
`execute_bundle()` function can process a list of up to eight instructions
for convenient use in fetch/decode unit testing.
