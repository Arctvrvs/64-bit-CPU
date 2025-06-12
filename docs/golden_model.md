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
  `SLLI`, `SRLI`, `SRAI`,
  32-bit forms `ADDW`, `SUBW`, `SLLW`, `SRLW`, `SRAW`,
  and immediates `ADDIW`, `SLLIW`, `SRLIW`, `SRAIW`,
  `LUI`, `AUIPC`)
- Load/store (`LB`/`LBU`, `LH`/`LHU`, `LW`/`LWU`, `LD`,
  `SB`, `SH`, `SW`, `SD`)
- Branches (`BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`)
- Jumps (`JAL`, `JALR`)
- Multiply/divide (`MUL`, `DIV`, `REM` and variants)
 - Floating-point add (`FADD.D`), subtract (`FSUB.D`), multiply (`FMUL.D`), divide (`FDIV.D`),
   min/max (`FMIN.D`/`FMAX.D`) and fused multiply-add/subtract
   (`FMADD.D`, `FMSUB.D`, `FNMSUB.D`, `FNMADD.D`)
- Atomic memory operations (`LR.D`, `SC.D`, `AMOADD.D`, `AMOSWAP.D`,
  `AMOXOR.D`, `AMOOR.D`, `AMOAND.D`, `AMOMIN.D`, `AMOMAX.D`,
  `AMOMINU.D`, `AMOMAXU.D`)
- Vector load/store (`vle64.v`, `vse64.v`), vector add (`vadd.vv`),
  vector multiply (`vmul.vv`) and vector fused multiply-add (`vfma.vv`)
- Gather/scatter instructions (`vluxei64.v`, `vsuxei64.v`) and helper
  methods (:py:meth:`~rtl.isa.golden_model.GoldenModel.gather`
  and :py:meth:`~rtl.isa.golden_model.GoldenModel.scatter`)
- CSR instructions (`CSRRW`, `CSRRS`, `CSRRC` and immediate forms)
- Barrier and system instructions (`FENCE`, `FENCE.I`, `ECALL`, `EBREAK`)
  and a speculative fetch fence (`SPEC_FENCE`) blocking loads until
  earlier branches retire

Misaligned load or store addresses raise a `"misalign"` exception which can be
queried via `get_last_exception()` after calling `step()`.
Accessing an unmapped address triggers a `"page"` exception.  The model
maintains a simple page table that maps virtual addresses to physical
locations.  `load_memory()` automatically creates identity mappings for
convenience and `map_page()` allows explicit virtual‐to‐physical entries.
Page walks record coverage when a `CoverageModel` instance is supplied.
Translations consult small L1 and L2 TLB helpers before falling back to the
page walker.  Misses refill both levels and the coverage model tracks TLB
hits, misses and the observed lookup latency.

When the optional virtualization control structure is active the model
translates physical addresses through the simplified EPT module before
accessing memory. `GoldenModel` creates a `VMCS` and `EPT` instance by
default so tests can enable virtualization via `vmcs.vm_on(vmid)`.
NX, SMEP and SMAP checks are also implemented so executing or accessing
user pages in supervisor mode raises the appropriate `"nx"`, `"smep"` or
`"smap"` exception depending on the page permissions and configuration
flags.
An `SGXEnclave` instance restricts memory accesses when enclave mode is
active; attempts to access addresses outside the enclave raise a
`"sgx"` exception.
Memory accesses go through a simple `SEVMemory` stub which XORs data and
addresses with a key to model AMD SEV style encryption.  The key can be
changed via :py:meth:`~rtl.isa.golden_model.GoldenModel.set_sev_key` and
the scoreboard handles decryption transparently.
Loads normally verify permissions before reading memory to model
Meltdown-style protection. This behavior can be toggled via
:py:meth:`~rtl.isa.golden_model.GoldenModel.set_meltdown_protect` for
tests that explore speculative side effects.

The `GoldenModel` class maintains an array of 32 general purpose registers,
a dictionary based memory and the current program counter. The `step` method
decodes and executes a single 32‑bit instruction. The helper
`execute_bundle()` function can process a list of instructions.  The higher
level helper `issue_bundle(pc, insts)` decodes up to eight instructions using
`Decoder8W`, executes them and returns the decoded µops, the next program
counter **and** a list of RAW/WAR/WAW hazards detected within the bundle.
