# Hash Crash

**Category:** Cryptography · Hash Cracking
**Difficulty:** Medium
**Points:** 500
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

During a breach investigation at CyberiumGrid Utilities Corp., analysts discovered that a critical system's password hash was inadvertently exposed in a configuration dump. The hash is stored without a salt — a critical mistake that makes offline cracking feasible.

The system is still live. If you can recover the plaintext password behind the hash, you can authenticate to the terminal and retrieve the classified access token stored inside.

Your mission: crack the hash and use it to gain access.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the hashing algorithm used |
| 2 | Recover the plaintext password from the hash |
| 3 | Authenticate to the terminal and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

You will see a terminal-style interface displaying a password hash. There is also an input field where you can submit a password. No files to download — everything is on screen.

**Your workflow:**
1. Identify the hash type from its format and length
2. Use an offline cracking tool against the hash
3. Enter the recovered password into the terminal interface

---

## Tools That May Help

- [Hashcat](https://hashcat.net/) — GPU-accelerated password recovery
- [John the Ripper](https://www.openwall.com/john/) — classic password cracking tool
- [CrackStation](https://crackstation.net/) — online lookup for common hashes
- [rockyou.txt](https://github.com/danielmiessler/SecLists) — the standard wordlist for CTF challenges
- Hash identification tools: `hash-identifier`, `hashid`

---

## Things to Think About

- Hash length and character set are strong indicators of the algorithm — look them up
- Unsalted hashes of common passwords often appear in precomputed lookup tables
- The rockyou.txt wordlist contains millions of real-world passwords — it's almost always the right starting point
- Hashcat format: `hashcat -m <mode> <hash> <wordlist>`

---

## Flag Format

```
CTF{...}
```

The flag is displayed on the terminal after successful authentication. Submit it on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
