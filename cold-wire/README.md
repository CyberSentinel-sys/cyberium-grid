# Cold Wire

**Category:** Cryptography · XOR Cipher
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

Grid incident responders recovered two files from an attacker's workstation after a breach at CyberiumGrid Utilities Corp. One file is an encrypted transmission — a classified shutdown command that was intercepted in transit. The second is a partial encryption tool recovered alongside it, but the key constant was wiped before it could be retrieved.

The encryption is simple — a single-byte XOR cipher. The key is somewhere in the noise. Your job is to find it and recover the original message.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the cipher algorithm used to encrypt the transmission |
| 2 | Identify the numeric value of the encryption key (decimal) |
| 3 | Decrypt the transmission and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download both files from the challenge interface:

| File | Description |
|------|-------------|
| `transmission.enc` | The encrypted transmission (binary) |
| `intercepted_tool.py` | Recovered encryption utility — key placeholder set to `0x00` |

Your goal is to determine the correct key and use the tool to decrypt the transmission.

---

## Tools That May Help

- Python 3 (built-in, no dependencies)
- A hex editor (e.g., `xxd`, `hexedit`, HxD)
- Basic understanding of XOR properties

---

## Things to Think About

- XOR encryption with a single byte key has a limited keyspace — how many possible keys exist?
- The decrypted plaintext should be readable ASCII text — what does that tell you about how to validate a candidate key?
- You can modify the `intercepted_tool.py` to test different key values
- The tool takes two arguments: `<input_file> <output_file>`

---

## Flag Format

```
CTF{...}
```

The flag is embedded in the decrypted plaintext. Submit it on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
