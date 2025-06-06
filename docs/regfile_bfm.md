# regfile_bfm Module

`regfile_bfm.py` implements a tiny bus functional model that verifies writes to
the architectural register file using the Python golden model. It can be used
by higher level UVM tests that observe the register file write ports.

The class exposes a `write()` method:

```python
from tb.uvm_components.regfile_bfm import RegFileBFM
bfm = RegFileBFM(start_pc=0)
ok = bfm.write(instr, rd_arch, rd_val)
```

Each call executes `instr` on an internal `GoldenModel` instance and compares the
result stored in register `rd_arch` with the value seen on the RTL write port.
`True` is returned when the value matches, otherwise `False`.

Use `reset()` to restart the model when beginning a new test sequence.
