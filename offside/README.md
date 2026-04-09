<div align="center">

# ░▒▓ OFFSIDE ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-FORENSICS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-EMAIL_ANALYSIS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
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
> An analyst at CyberiumGrid Utilities Corp. received an unsolicited email —
> a ticket confirmation that arrived from an unrecognized external address.
> Something about it felt wrong. Before deleting it, she forwarded it to the
> security team with a single note: *"Don't think this is what it looks like."*
>
> She was right.
>
> Standard mail clients showed nothing unusual. A clean-looking confirmation email.
> Ticket number, event details, a polite sign-off. Completely benign on the surface.
>
> But threat actors don't hide in the body of emails anymore. They hide in the headers —
> fields your mail client never shows you, fields that get logged and forgotten.
> Somewhere in the raw RFC 5322 structure of this message is a hidden payload
> that was never meant to be found.
>
> **Open the raw file. Read between the lines — literally.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **name of the custom header** containing the hidden data | `LOCKED` |
| `M-02` | Identify the **encoding scheme** used to encode the value in that header | `LOCKED` |
| `M-03` | Decode the value and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download the email file from the challenge interface:

```
┌──────────────────────────────┬────────────────────────────────────────────┐
│ FILE                         │ DESCRIPTION                                │
├──────────────────────────────┼────────────────────────────────────────────┤
│ ticket_confirmation.eml      │ Raw email file in RFC 5322 format          │
└──────────────────────────────┴────────────────────────────────────────────┘
```

> **Critical:** Open this file in a **plain text editor** — not an email client.
> You need the raw headers. An email client will render the visible body and
> hide everything that matters. Use `cat`, `nano`, `vim`, VS Code, or Notepad++.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Plain text editor (nano, vim, VS Code, Notepad++)
▸  cat / strings / grep — command-line inspection
▸  base64 -d (Linux) or any online decoder
```

[![Forensics](https://img.shields.io/badge/TOOL-TEXT_EDITOR_+_BASE64-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — Where do you look in the raw email?</strong></summary>

<br>

Email headers appear at the top of the `.eml` file, before the message body. Standard headers include `From`, `To`, `Subject`, `Date`, and `Message-ID`. Custom headers that don't belong to the RFC standard often start with `X-`.

</details>

<details>
<summary><strong>▶ Hint 2 — What encoding scheme is commonly used in email headers?</strong></summary>

<br>

Email is a text-based protocol. When binary or arbitrary data needs to be embedded, it's typically encoded using a scheme that outputs only printable ASCII characters. One encoding scheme is ubiquitous in this context.

</details>

<details>
<summary><strong>▶ Hint 3 — How do you decode it?</strong></summary>

<br>

On Linux: `echo "ENCODED_VALUE" | base64 -d`
On any OS: paste the value into an online base64 decoder.
The decoded output will contain the flag.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the decoded value of the hidden custom header.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
