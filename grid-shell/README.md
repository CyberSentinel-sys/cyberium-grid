<div align="center">

# ░▒▓ GRID SHELL ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-WEB_EXPLOITATION-2563eb?style=for-the-badge&logo=firefox)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-COMMAND_INJECTION-2563eb?style=for-the-badge&logo=firefox)](https://cyberium.io)
[![Difficulty](https://img.shields.io/badge/DIFFICULTY-HARD-dc2626?style=for-the-badge)](https://cyberium.io)
[![Points](https://img.shields.io/badge/POINTS-600-6d28d9?style=for-the-badge)](https://cyberium.io)
[![Platform](https://img.shields.io/badge/PLATFORM-CYBERIUM_ARENA-0f172a?style=for-the-badge&logo=docker)](https://cyberium.io)

<br>

</div>

---

## ╔══════════════════════════════╗
## ║   THREAT INTELLIGENCE FILE   ║
## ╚══════════════════════════════╝

> **CLASSIFICATION: TOP SECRET — CLEARED OPERATORS ONLY**
>
> CyberiumGrid Utilities Corp. deployed an internal network diagnostic tool
> for field operators. The interface is simple: enter an IP address, get a
> connectivity report. Fast, convenient, trusted.
>
> The developers made one assumption: that operators would only ever enter
> valid IP addresses into the input field.
>
> That assumption is a vulnerability.
>
> Behind the clean UI, the application takes your input and hands it directly
> to the operating system. No sanitization. No allowlist. No escape.
> The shell doesn't know you're not supposed to be there.
> It just executes.
>
> The flag is sitting at `/flag.txt` on the server.
> One crafted input is all that stands between you and it.
> **Make the server do something it wasn't designed to do.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **vulnerability class** present in the diagnostic tool | `LOCKED` |
| `M-02` | Craft an input that **executes an additional command** alongside the intended operation | `LOCKED` |
| `M-03` | Read `/flag.txt` from the server and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   OPERATIONAL PARAMETERS     ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

You will see a web interface with a single input field — a network diagnostic tool that accepts a target address. **No files to download.** Everything happens in the browser.

**Attack surface:**

```
┌──────────────────────────────────────────┐
│  TARGET: Web input field (diagnostic UI) │
│  SERVER: Linux — flag at /flag.txt       │
│  BACKEND: Passes input to OS command     │
│  DEFENSE: None detected                  │
└──────────────────────────────────────────┘
```

> **Start by submitting a normal IP address** to understand how the tool responds.
> Observe the output. Think about what the server-side command looks like.
> Then think about what happens when your input contains more than just an IP address.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Web browser with Developer Tools (F12)
▸  Burp Suite — intercept and replay modified requests
▸  Knowledge of Linux shell metacharacters and command chaining
```

[![Burp Suite](https://img.shields.io/badge/TOOL-BURP_SUITE-2563eb?style=for-the-badge&logo=firefox)](https://portswigger.net/burp)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — What is the vulnerability class?</strong></summary>

<br>

When a web application passes unsanitized user input to a system shell command, attackers can inject additional shell instructions. This class of vulnerability has a well-known name — look it up in OWASP or CVE databases.

</details>

<details>
<summary><strong>▶ Hint 2 — How does Linux chaining work?</strong></summary>

<br>

Linux shells support multiple characters that allow you to chain commands together. Characters like `;`, `&&`, `||`, and the backtick or `$()` subshell notation can all be used to append additional commands to the one the application intended to run.

</details>

<details>
<summary><strong>▶ Hint 3 — What command reads a file?</strong></summary>

<br>

The flag is at `/flag.txt`. The Linux command `cat` reads the contents of a file to standard output. Combine a chaining character with `cat /flag.txt` and inject it into the input field.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the contents of `/flag.txt` on the remote server.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
