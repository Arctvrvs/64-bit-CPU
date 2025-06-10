# top Module

`top.sv` is the entry point for full-chip simulation. It instantiates the
`riscv_soc_4core` module and simply wires up the shared clock and reset
signals. The SystemVerilog RTL is only a thin wrapper but provides a
consistent top-level for future synthesis or more complete SoC models.

The matching Python stub `Top` offers a small helper for unit tests that
steps the underlying SoC model.  It can be imported directly from the
`tb.uvm_components` package:

```python
from tb.uvm_components import Top

t = Top()
t.step()
```
