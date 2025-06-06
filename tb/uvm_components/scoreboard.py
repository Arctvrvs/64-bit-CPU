class Scoreboard:
    """Very small scoreboard for unit tests."""

    def __init__(self):
        self.expected = []
        self.actual = []

    def add_expected(self, value):
        self.expected.append(value)

    def add_actual(self, value):
        self.actual.append(value)

    def check(self):
        return self.expected == self.actual
