# Serpent

**Category:** Forensics · Malware Static Analysis
**Difficulty:** Medium
**Points:** 500
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

Incident responders at CyberiumGrid Utilities Corp. recovered a suspicious Python script from a compromised workstation. The script appears to be a piece of malware — obfuscated to resist casual inspection. Variable names have been mangled, constants are hidden behind encoding layers, and the code establishes a connection to an external command-and-control server.

Static analysis is the first step. You don't need to run it — in fact, you shouldn't. Read it, understand it, and extract what's hidden inside.

Your mission: reverse the obfuscation, identify the encoding used to hide the payload, and decode it to retrieve the flag.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the encoding scheme applied to the hidden payload constant |
| 2 | Count the total number of obfuscated variable/constant names in the script |
| 3 | Decode the hidden payload and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download the malware sample from the challenge interface:

| File | Description |
|------|-------------|
| `grid_implant.py` | Recovered Python script — suspected C2 implant |

**Do not execute this script.** Analyze it statically — read the source code and understand the logic without running it.

---

## Tools That May Help

- Any text editor or IDE (VS Code, vim, nano)
- Python 3 (for manual decoding in a safe interpreter)
- `base64` module in Python or `base64 -d` on Linux
- Understanding of Python lambda functions and byte manipulation

---

## Things to Think About

- Focus on the obfuscated constants — what do `_1ll`, `_lll`, and similar names represent?
- One constant is a base64-encoded string. Another is a single byte used as an XOR key. Trace the logic.
- The "recovered payload" is decoded in the script itself — follow the variable assignments step by step
- For Mission 2: count every variable or constant that uses the obfuscated naming pattern (`_l1l`, `_1ll`, etc.)
- You can safely decode the payload manually in a Python shell without executing the malicious parts

---

## Flag Format

```
CTF{...}
```

The decoded payload contains the flag. Submit it on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
