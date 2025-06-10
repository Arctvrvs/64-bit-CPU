# Golden Model

The `golden_model.py` file located under `rtl/isa` provides a tiny reference
implementation of a 64‑bit RISC‑V interpreter. It is not cycle accurate but
implements a minimal subset of RV64I so that UVM testbenches can compare
results against expected behavior.

Currently supported instructions include:

- Integer ALU operations (`ADD`, `SUB`, `AND`, `OR`, `XOR`,
  `SLL`, `SRL`, `SRA`, `SLT`, `SLTU`,
  `ADDI`, `ANDI`, `ORI`, `XORI`,
  `SLTI`, `SLTIU`,
  `SLLI`, `SRLI`, `SRAI`, `LUI`, `AUIPC`)
- Load/store (`LB`/`LBU`, `LH`/`LHU`, `LW`/`LWU`, `LD`,
  `SB`, `SH`, `SW`, `SD`)
- Branches (`BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`)
- Jumps (`JAL`, `JALR`)
- Multiply/divide (`MUL`, `DIV`, `REM` and variants)
- Floating-point add (`FADD.D`)
- Basic atomic operations (`LR.D`, `SC.D`, `AMOADD.D`, `AMOSWAP.D`)
- Vector load/store (`vle64.v`, `vse64.v`) and vector add (`vadd.vv`)
- CSR instructions (`CSRRW`, `CSRRS`, `CSRRC` and immediate forms)

Misaligned load or store addresses raise a `"misalign"` exception which can be
queried via `get_last_exception()` after calling `step()`.
Accessing an unmapped address triggers a `"page"` exception.  The model
maintains a simple page table that maps virtual addresses to physical
locations.  `load_memory()` automatically creates identity mappings for
convenience and `map_page()` allows explicit virtual‐to‐physical entries.
Page walks record coverage when a `CoverageModel` instance is supplied.

Misaligned load or store addresses raise a `"misalign"` exception which can be
queried via `get_last_exception()` after calling `step()`.

The `GoldenModel` class maintains an array of 32 general purpose registers,
a dictionary based memory and the current program counter. The `step` method
decodes and executes a single 32‑bit instruction. The helper
`execute_bundle()` function can process a list of instructions.  The higher
level helper `issue_bundle(pc, insts)` decodes up to eight instructions using
`Decoder8W`, executes them and returns the decoded µops, the next program
counter **and** a list of RAW/WAR/WAW hazards detected within the bundle.
