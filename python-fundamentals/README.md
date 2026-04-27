<div align="center">

# ░▒▓ REMNANT ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-PYTHON_FUNDAMENTALS-2563eb?style=for-the-badge&logo=python)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-CODE_TRACING-2563eb?style=for-the-badge&logo=python)](https://cyberium.io)
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
> **INCIDENT REF:** CG-2026-0041
> **SITE:** CyberiumGrid Utilities Corp. — Northern Operations Center
> **ASSET:** Grid operator workstation, host `NOC-WS-07`
> **REPORTED BY:** Incident Response Team Alpha

---

At 03:17 local time, an anomaly alert flagged brief interactive access on workstation `NOC-WS-07` — a machine assigned to a grid operator who was not on shift.

Forensic responders reached the workstation before it could be reimaged. The session had already ended. No lateral movement was detected. No network connections were logged during the access window. No files were transferred out.

What they found was a single Python script left behind in the operator's temporary directory:

```
/tmp/.cache/proc/recovered_script.py
```

The script is short. It is not obfuscated. It does not contact external hosts. It takes a hardcoded sequence of integers, processes them one by one, assembles a result, and prints it.

The attacker ran it, read the output, and left.

Your job is to read the same code — understand what it does, trace what it produces, and recover the exact output the attacker saw on screen.

**Every value in this script is deterministic. Every step can be followed without running a single command.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE |
|:-------:|-----------|
| `M-01` | What is the name of the Python built-in function used to convert each integer in the list into a character? |
| `M-02` | How many segments does the final output string contain when split by the `_` character? |
| `M-03` | Submit the flag — `CTF{...}` |

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

Download the artifact from the challenge interface on Cyberium Arena:

```
┌──────────────────────┬──────────────────────────────────────────────────────┐
│ FILE                 │ DESCRIPTION                                          │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ recovered_script.py  │ Python script recovered from NOC-WS-07 temp directory│
│                      │ Contains a hardcoded integer sequence and processing  │
│                      │ logic. Output is the target of this investigation.    │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

> `recovered_script.py` is also included in this repository for reference.

---

## ╔══════════════════════════════╗
## ║   TECHNICAL CONTEXT          ║
## ╚══════════════════════════════╝

The script follows a straightforward pattern common in Python:

- A list of **integer values** is defined
- Each integer is **converted into a character** using a Python built-in
- The characters are **joined into a single string**
- The string is **split on a delimiter** and the number of resulting segments is printed
- The **full assembled string** is printed as the final output

Understanding how Python maps integers to characters is central to this challenge. The relevant concepts are covered in the **Python Field Kit** intel article.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Python 3 interpreter
▸  Text editor or IDE (VS Code, vim, nano)
▸  Python documentation — docs.python.org
▸  ASCII reference table
```

[![Python](https://img.shields.io/badge/TOOL-PYTHON_3-2563eb?style=for-the-badge&logo=python)](https://python.org)

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the exact string printed as the final output of the recovered script.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
