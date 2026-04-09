<div align="center">

# ░▒▓ SERPENT ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-FORENSICS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-MALWARE_STATIC_ANALYSIS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Difficulty](https://img.shields.io/badge/DIFFICULTY-MEDIUM-d97706?style=for-the-badge)](https://cyberium.io)
[![Points](https://img.shields.io/badge/POINTS-500-6d28d9?style=for-the-badge)](https://cyberium.io)
[![Platform](https://img.shields.io/badge/PLATFORM-CYBERIUM_ARENA-0f172a?style=for-the-badge&logo=docker)](https://cyberium.io)

<br>

</div>

---

## ╔══════════════════════════════╗
## ║   THREAT INTELLIGENCE FILE   ║
## ╚══════════════════════════════╝

> **CLASSIFICATION: TOP SECRET — CLEARED ANALYSTS ONLY**
>
> Incident responders at CyberiumGrid Utilities Corp. recovered a suspicious
> Python script from a compromised operator workstation. First pass: it looks
> like gibberish. Variable names mangled. Constants buried under encoding layers.
> A connection attempt to an external C2 server that's already been sinkholed.
>
> This is a custom implant. Someone wrote it to survive casual inspection.
> The variable names are deliberately obfuscated — `_1ll`, `_lll`, `_l1l` —
> designed to be visually confusing, difficult to trace, impossible to Google.
>
> But obfuscation isn't encryption. The logic is still there.
> The payload is still inside — encoded, layered, waiting to be peeled back.
>
> **You don't run malware. You read it.**
> **Static analysis only. Understand the obfuscation. Decode the payload. Extract the flag.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **encoding scheme** applied to the hidden payload constant | `LOCKED` |
| `M-02` | Count the total number of **obfuscated variable/constant names** in the script | `LOCKED` |
| `M-03` | Decode the hidden payload and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download the malware sample from the challenge interface:

```
┌──────────────────────┬──────────────────────────────────────────────────────┐
│ FILE                 │ DESCRIPTION                                          │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ grid_implant.py      │ Recovered Python script — suspected C2 implant       │
│                      │ Obfuscated variable names, encoded payload constant  │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

> **CRITICAL: Do not execute this script.**
> Analyze it statically — read the source code and understand the logic without running it.
> You can safely decode the payload manually in a Python interpreter.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Text editor or IDE (VS Code, vim, nano) — read the source
▸  Python 3 interpreter — for safely decoding constants in isolation
▸  base64 module in Python — import base64; base64.b64decode(...)
▸  Understanding of Python lambda functions and byte operations
```

[![Python](https://img.shields.io/badge/TOOL-PYTHON_3_STATIC_ONLY-059669?style=for-the-badge&logo=python)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — How to read obfuscated Python</strong></summary>

<br>

Start by ignoring the confusing variable names. Trace the data flow instead — find the constants (string literals and integer values) and follow how they're used. One constant is a long encoded string. Another is a short integer used as a key. The logic that combines them is the decryption routine.

</details>

<details>
<summary><strong>▶ Hint 2 — What encoding layers are present?</strong></summary>

<br>

The payload uses two layers: a common text-to-binary encoding scheme applied first, and a single-byte XOR operation applied on top. Trace the variable assignments in order — the script decodes its own payload before using it. Follow the same steps manually.

</details>

<details>
<summary><strong>▶ Hint 3 — Counting obfuscated names for Mission 2</strong></summary>

<br>

The obfuscated naming pattern uses combinations of `_`, `l`, `1`, and similar visually confusing characters (e.g., `_1ll`, `_lll`, `_l1l`). Count every unique variable or constant name that follows this pattern throughout the script. Be methodical — read line by line.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is contained in the decoded payload string.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
