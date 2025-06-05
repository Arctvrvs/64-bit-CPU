# instr_memory_model Module

`instr_memory_model.py` implements a tiny instruction memory used by the
Python testbench. Internally it relies on the `DRAMModel` so that the
same backing storage can be shared with a data memory model if needed.

## Usage

```python
from tb.uvm_components.instr_memory_model import InstructionMemoryModel
imem = InstructionMemoryModel()
imem.load_program(0x1000, [0x00500093, 0x00300113])
first = imem.fetch(0x1000)
```

`load_program(addr, instructions)` loads a list of 32‑bit instruction words
starting at `addr`. The `fetch(addr)` method returns the instruction at the
address or zero if none was stored.
