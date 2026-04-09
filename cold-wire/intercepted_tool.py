#!/usr/bin/env python3
"""
Encryption utility — partial recovery from attacker workstation.
The key constant has been wiped from this copy.
"""


def xor_cipher(data: bytes, key: int) -> bytes:
    """Apply single-byte XOR cipher. Encryption and decryption are identical."""
    return bytes(b ^ key for b in data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_file> <output_file>")
        sys.exit(1)

    key = 0x00  # PLACEHOLDER — recover the correct single-byte key

    with open(sys.argv[1], "rb") as fh:
        raw = fh.read()

    result = xor_cipher(raw, key)

    with open(sys.argv[2], "wb") as fh:
        fh.write(result)

    print(f"[+] Processed {len(raw)} bytes with key 0x{key:02X}")
