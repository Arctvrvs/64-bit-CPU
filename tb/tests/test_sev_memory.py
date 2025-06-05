from rtl.security.sev_memory import SEVMemory


def test_encrypt_decrypt():
    sev = SEVMemory(key=0xDEADBEEFDEADBEEF)
    plain = 0x1122334455667788
    enc = sev.encrypt(plain)
    assert enc == plain ^ 0xDEADBEEFDEADBEEF
    sev.set_key(0xAA)
    enc2 = sev.encrypt(plain)
    dec2 = sev.decrypt(enc2)
    assert dec2 == plain
