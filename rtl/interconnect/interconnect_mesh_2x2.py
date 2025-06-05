class InterconnectMesh2x2:
    """Very small 2x2 mesh model that routes packets by destination index."""
    def __init__(self):
        self.pending = [[] for _ in range(4)]

    def send(self, src_idx, dest_idx, data):
        self.pending[dest_idx].append({'src': src_idx, 'data': data})

    def step(self):
        outputs = [list(pkts) for pkts in self.pending]
        self.pending = [[] for _ in range(4)]
        return outputs

