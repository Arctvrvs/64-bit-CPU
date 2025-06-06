# sev_memory Module

`sev_memory.sv` provides a placeholder for AMD SEV style memory encryption. It simply XORs data with a per-VM key when writing to or reading from DRAM.

## Ports

| Name | Dir | Width | Description |
|------|-----|-------|-------------|
| `key_i` | in | 64 | Encryption key selected for the current VM |
| `data_in_i` | in | 64 | Plaintext data to encrypt |
| `enc_data_o` | out | 64 | Ciphertext after XOR with key |
| `data_enc_i` | in | 64 | Ciphertext read from memory |
| `dec_data_o` | out | 64 | Decrypted plaintext |

## Behavior

Both encryption and decryption are combinational: `enc_data_o = data_in_i ^ key_i` and `dec_data_o = data_enc_i ^ key_i`. The stub does not model key management or timing delays but allows unit tests to mimic SEV style data protection.
