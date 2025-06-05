# reset_generator Module

`reset_generator.py` provides a small helper used by the Python tests to
produce an active-low reset signal for a configurable number of cycles.

```python
from tb.uvm_components.reset_generator import ResetGenerator
rst = ResetGenerator(cycles=3)
value0 = rst.get()     # 0 at cycle 0
value1 = rst.tick()    # advance one cycle
```

After `cycles` ticks the generated `rst_n` value changes to `1` and stays
asserted on subsequent calls. The `reset()` method restarts the pulse
so that another sequence can be generated.
