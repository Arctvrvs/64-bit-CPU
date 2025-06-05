# data_memory_model Module

`data_memory_model.py` implements a tiny data memory used by the Python
unit tests. Like the instruction memory model it relies on the
`DRAMModel` so that tests can share the same backing storage.

## Usage

```python
from tb.uvm_components.data_memory_model import DataMemoryModel
mem = DataMemoryModel()
mem.store(0x100, 0x1122334455667788)
val = mem.load(0x100)
```

The optional `size` argument to `store` and `load` specifies the number of
bytes (1, 2, 4 or 8) to access. Any unused bits are masked.
