<div align="center">

# ░▒▓ COLD WIRE ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-CRYPTOGRAPHY-0891b2?style=for-the-badge&logo=gnupg)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-XOR_CIPHER-0891b2?style=for-the-badge&logo=gnupg)](https://cyberium.io)
[![Difficulty](https://img.shields.io/badge/DIFFICULTY-EASY-16a34a?style=for-the-badge)](https://cyberium.io)
[![Points](https://img.shields.io/badge/POINTS-400-6d28d9?style=for-the-badge)](https://cyberium.io)
[![Platform](https://img.shields.io/badge/PLATFORM-CYBERIUM_ARENA-0f172a?style=for-the-badge&logo=docker)](https://cyberium.io)

<br>

</div>

---

## ╔══════════════════════════════╗
## ║   THREAT INTELLIGENCE FILE   ║
## ╚══════════════════════════════╝

> **CLASSIFICATION: RESTRICTED — AUTHORIZED ANALYSTS ONLY**
>
> Grid incident responders executed a rapid seizure of an attacker's workstation
> following a breach at CyberiumGrid Utilities Corp. Two files were recovered before
> the drive could be wiped.
>
> The first: an encrypted binary transmission — a classified grid shutdown command
> that was intercepted mid-transit and scrambled before delivery.
>
> The second: a partial encryption tool. The key constant was zeroed out — deliberately
> erased in the final seconds before seizure. Someone knew we were coming.
>
> The cipher is elementary. A single byte. Somewhere between 0 and 255.
> The key is in the noise. The message is in the dark.
> **Find the key. Recover the transmission. Extract what was meant to stay buried.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **cipher algorithm** used to encrypt the transmission | `LOCKED` |
| `M-02` | Determine the **numeric value of the encryption key** (decimal) | `LOCKED` |
| `M-03` | Decrypt the transmission and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download both files from the challenge interface:

```
┌──────────────────────┬──────────────────────────────────────────────────┐
│ FILE                 │ DESCRIPTION                                      │
├──────────────────────┼──────────────────────────────────────────────────┤
│ transmission.enc     │ Encrypted binary transmission — the target       │
│ intercepted_tool.py  │ Recovered encryption utility — key set to 0x00  │
└──────────────────────┴──────────────────────────────────────────────────┘
```

> `intercepted_tool.py` is also available in this repository for reference.
> Determine the correct key and use the tool to decrypt `transmission.enc`.
> The tool accepts two arguments: `<input_file> <output_file>`

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Python 3 — no external dependencies required
▸  xxd or hexedit — inspect raw bytes in the encrypted file
▸  A text editor — to modify the key constant in intercepted_tool.py
```

[![Python](https://img.shields.io/badge/TOOL-PYTHON_3-0891b2?style=for-the-badge&logo=python)](https://python.org)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — How large is the keyspace?</strong></summary>

<br>

A single-byte XOR key has a very limited range of possible values. Exactly 256 candidates. That's a small enough space to test systematically.

</details>

<details>
<summary><strong>▶ Hint 2 — How do you know when you've found the right key?</strong></summary>

<br>

A correctly decrypted transmission should produce readable ASCII text — human-readable content with recognizable characters. Invalid keys will produce garbage bytes. Look for a result that makes sense as text.

</details>

<details>
<summary><strong>▶ Hint 3 — How do you test each candidate key?</strong></summary>

<br>

Modify the key constant in `intercepted_tool.py` and run it on `transmission.enc`. Try different values. When the output looks like readable text containing the flag format `CTF{...}`, you've found it.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is embedded in the decrypted plaintext transmission.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
