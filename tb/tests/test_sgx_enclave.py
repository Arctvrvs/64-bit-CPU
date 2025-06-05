from rtl.security.sgx_enclave import SGXEnclave


def test_enclave_flow():
    sgx = SGXEnclave()
    sgx.ecreate(0x1000)
    sgx.eadd(0x1000, 0xdeadbeef)
    sgx.einit()
    sgx.eenter()
    assert sgx.access(0x1000) is False
    assert sgx.access(0x2000) is True
    sgx.eexit()
    assert sgx.access(0x2000) is False
