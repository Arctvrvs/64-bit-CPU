class ExStage:
    """Simple execution stage model mimicking ex_stage.sv."""

    def __init__(self):
        self.pending = [None] * 8

    def cycle(self, issues):
        wb = [None] * 8
        # advance counters
        for i, ent in enumerate(self.pending):
            if ent is not None:
                ent['count'] -= 1
        # load new issues
        for j, issue in enumerate(issues):
            if issue is not None:
                fu = issue['fu']
                dest = issue['dest']
                rob = issue['rob']
                op1 = issue['op1']
                op2 = issue['op2']
                if fu == 0:
                    data = op1 + op2
                    count = 1
                else:
                    data = 0
                    count = 3
                self.pending[j] = {'data': data, 'dest': dest, 'rob': rob, 'count': count}
        # produce results
        for k, ent in enumerate(self.pending):
            if ent is not None and ent['count'] <= 0:
                wb[k] = {'data': ent['data'], 'dest': ent['dest'], 'rob': ent['rob']}
                self.pending[k] = None
        return wb
