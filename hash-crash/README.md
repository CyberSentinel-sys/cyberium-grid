<div align="center">

# ░▒▓ HASH CRASH ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-CRYPTOGRAPHY-0891b2?style=for-the-badge&logo=gnupg)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-HASH_CRACKING-0891b2?style=for-the-badge&logo=gnupg)](https://cyberium.io)
[![Difficulty](https://img.shields.io/badge/DIFFICULTY-MEDIUM-d97706?style=for-the-badge)](https://cyberium.io)
[![Points](https://img.shields.io/badge/POINTS-500-6d28d9?style=for-the-badge)](https://cyberium.io)
[![Platform](https://img.shields.io/badge/PLATFORM-CYBERIUM_ARENA-0f172a?style=for-the-badge&logo=docker)](https://cyberium.io)

<br>

</div>

---

## ╔══════════════════════════════╗
## ║   THREAT INTELLIGENCE FILE   ║
## ╚══════════════════════════════╝

> **CLASSIFICATION: RESTRICTED — AUTHORIZED ANALYSTS ONLY**
>
> A configuration dump from a compromised CyberiumGrid Utilities Corp. system
> was recovered during a breach investigation. Inside it: a password hash.
>
> Whoever set this up made a critical error. No salt. No iterations.
> Just a raw hash of whatever password they chose — exposed in plaintext
> in a configuration file that wasn't supposed to leave the server.
>
> The system it protects is still live. The terminal is still accepting logins.
> The classified access token is still sitting behind that password, waiting.
>
> A hash is a one-way function — you can't reverse it mathematically.
> But if the password came from a human? Humans are predictable.
> Humans reuse passwords. Humans choose passwords that are already in databases
> compiled from a decade of breaches.
>
> The hash is on screen. The wordlist exists.
> **Crack it. Authenticate. Take the flag.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **hashing algorithm** used to produce the hash | `LOCKED` |
| `M-02` | **Recover the plaintext password** from the hash | `LOCKED` |
| `M-03` | Authenticate to the terminal and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   OPERATIONAL PARAMETERS     ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

You will see a terminal-style interface displaying a password hash and a password input field. **No files to download.** Everything is on screen.

**Workflow:**

```
┌──────────────────────────────────────────────────────┐
│  STEP 1 — Read the hash displayed on the terminal    │
│  STEP 2 — Identify the algorithm from hash format    │
│  STEP 3 — Crack the hash offline with a wordlist     │
│  STEP 4 — Enter the recovered password in the UI     │
│  STEP 5 — Collect the flag from the authenticated    │
│           terminal session                           │
└──────────────────────────────────────────────────────┘
```

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  hashcat — GPU-accelerated password recovery (hashcat.net)
▸  John the Ripper — classic CPU-based cracker
▸  CrackStation — online lookup for common unsalted hashes
▸  rockyou.txt — the standard CTF wordlist (millions of real passwords)
▸  hash-identifier / hashid — identify algorithm from hash format
```

[![Hashcat](https://img.shields.io/badge/TOOL-HASHCAT-0891b2?style=for-the-badge&logo=gnupg)](https://hashcat.net)
[![CrackStation](https://img.shields.io/badge/TOOL-CRACKSTATION-0891b2?style=for-the-badge&logo=gnupg)](https://crackstation.net)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — How do you identify the hash algorithm?</strong></summary>

<br>

Hash algorithms produce outputs of fixed, predictable lengths. MD5 produces 32 hex characters. SHA-1 produces 40. SHA-256 produces 64. The format of the hash — length and character set — is usually enough to identify the algorithm. Tools like `hash-identifier` or `hashid` can confirm your guess.

</details>

<details>
<summary><strong>▶ Hint 2 — What's the fastest way to crack it?</strong></summary>

<br>

Unsalted hashes of common passwords are often in precomputed lookup tables. Try [CrackStation](https://crackstation.net) first — paste the hash and it will check against billions of known hash-to-password mappings instantly. If that fails, use `hashcat` with `rockyou.txt`.

</details>

<details>
<summary><strong>▶ Hint 3 — Hashcat syntax for dictionary attack</strong></summary>

<br>

```
hashcat -m <mode_number> <hash> /path/to/rockyou.txt
```

The `-m` flag specifies the hash type. Look up the correct mode number for the algorithm you identified. Hashcat will print the cracked password when it finds a match.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is displayed on the terminal after successful authentication.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
