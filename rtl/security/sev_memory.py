class SEVMemory:
    """Tiny model performing XOR encryption with a key."""
    def __init__(self, key=0):
        self.key = key & 0xFFFFFFFFFFFFFFFF

    def set_key(self, key: int):
        self.key = key & 0xFFFFFFFFFFFFFFFF

    def encrypt(self, data: int) -> int:
        return data ^ self.key

    def decrypt(self, data: int) -> int:
        return data ^ self.key
