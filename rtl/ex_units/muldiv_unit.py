class MulDivUnit:
    """Python model of muldiv_unit with simple latency pipelines."""

    def __init__(self, mul_latency=3, div_latency=20):
        self.mul_latency = mul_latency
        self.div_latency = div_latency
        self.mul_pipe = []
        self.div_pipe = []

    def cycle(self, mul_op=None, div_op=None):
        """Advance pipelines one cycle and optionally issue new ops.

        ``mul_op`` and ``div_op`` are dictionaries with keys ``op_a``,
        ``op_b``/``dividend``/``divisor``, ``dest`` and ``rob``.
        Returns a tuple ``(mul_result, div_result)`` where each result is
        a dictionary with ``result``, ``dest`` and ``rob`` or ``None``.
        """
        # insert new operations
        if mul_op is not None:
            res = (mul_op.get("op_a", 0) * mul_op.get("op_b", 0)) & 0xFFFFFFFFFFFFFFFF
            self.mul_pipe.append({
                "count": self.mul_latency,
                "result": res,
                "dest": mul_op.get("dest"),
                "rob": mul_op.get("rob"),
            })
        if div_op is not None:
            divisor = div_op.get("divisor", 0)
            if divisor == 0:
                res = 0
            else:
                res = (div_op.get("dividend", 0) // divisor) & 0xFFFFFFFFFFFFFFFF
            self.div_pipe.append({
                "count": self.div_latency,
                "result": res,
                "dest": div_op.get("dest"),
                "rob": div_op.get("rob"),
            })

        # step pipelines
        for ent in self.mul_pipe:
            ent["count"] -= 1
        for ent in self.div_pipe:
            ent["count"] -= 1

        mul_result = None
        div_result = None
        if self.mul_pipe and self.mul_pipe[0]["count"] <= 0:
            mul_result = self.mul_pipe.pop(0)
        if self.div_pipe and self.div_pipe[0]["count"] <= 0:
            div_result = self.div_pipe.pop(0)

        return mul_result, div_result
