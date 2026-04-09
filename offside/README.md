# Offside

**Category:** Network Forensics · Email Analysis
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

An analyst at CyberiumGrid Utilities Corp. received a suspicious email — a ticket confirmation that arrived from an unrecognized sender. Before deleting it, they forwarded it to the security team for analysis.

Initial review suggests the email is more than it appears. Threat actors have been known to hide authentication tokens and exfiltrated data inside email headers — fields that standard mail clients never display to the user.

Your mission: examine the raw email and find what's hidden inside.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the name of the custom HTTP/email header containing the hidden data |
| 2 | Identify the encoding scheme used to encode the value in that header |
| 3 | Decode the value and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download the email file from the challenge interface:

| File | Description |
|------|-------------|
| `ticket_confirmation.eml` | Raw email file in RFC 5322 format |

Open the file in a **text editor** — not an email client. You need to see the raw headers, not the rendered email.

---

## Tools That May Help

- Any plain text editor (`nano`, `vim`, VS Code, Notepad++)
- Command line tools: `cat`, `strings`, `grep`
- A base64 decoder (`base64 -d` on Linux, or any online decoder)

---

## Things to Think About

- Standard email clients hide custom headers from users — look for fields that start with `X-`
- Email headers are plain text and appear at the top of the `.eml` file before the message body
- Common encoding schemes used to carry binary data in text-based formats include base64

---

## Flag Format

```
CTF{...}
```

Submit the decoded flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
