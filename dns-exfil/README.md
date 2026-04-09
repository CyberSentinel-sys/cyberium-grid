<div align="center">

# ░▒▓ DNS EXFIL ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-FORENSICS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-NETWORK_ANALYSIS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
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
> 02:34 local time. The network security team at CyberiumGrid Utilities Corp.
> caught an anomaly on the outbound traffic sensor — a quiet, sustained pulse
> of DNS queries during a maintenance window when no operators were active.
>
> A packet capture was taken at the DNS resolver. Hundreds of entries.
> Most of them clean — routine lookups for internal grid services, update servers,
> monitoring endpoints. The kind of traffic that fills every corporate log file
> and gets archived without a second look.
>
> But DNS is a strange protocol to use for exfiltration, and yet it works every time.
> Firewalls almost never block port 53. DNS is trusted by default. And the subdomain
> portion of a DNS query? That's just text. Any text you want.
>
> Someone tunneled data out of the network by encoding it into DNS subdomains —
> splitting a payload across dozens of queries, each one looking like a slightly
> unusual but plausible domain lookup. Invisible to anything that wasn't specifically
> looking for the pattern.
>
> **The data left the building. Find the channel. Decode the chunks. Recover what was stolen.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **source IP address** of the attacker performing the exfiltration | `LOCKED` |
| `M-02` | Identify the **encoding scheme** used in the DNS subdomain queries | `LOCKED` |
| `M-03` | Decode the exfiltrated data chunks and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download the network capture from the challenge interface:

```
┌─────────────────┬──────────────────────────────────────────────────────────┐
│ FILE            │ DESCRIPTION                                              │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ capture.log     │ DNS query log — tab-separated, ~100 entries              │
│                 │ Human-readable text format — no special tools needed     │
└─────────────────┴──────────────────────────────────────────────────────────┘
```

> Open in any text editor or analyze with command-line tools.
> The log records source IP, timestamp, and queried domain for each DNS request.
> Most queries are routine — one source IP is not.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Text editor — initial review of the log
▸  grep / sort / uniq -c — filter entries by source IP, identify anomalies
▸  awk / cut — extract specific columns (source IP, queried domain)
▸  base64 -d (Linux) or online decoder — decode the exfiltrated content
▸  Python — script the extraction if the data spans many queries
```

[![Forensics](https://img.shields.io/badge/TOOL-GREP_+_AWK_+_BASE64-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Python](https://img.shields.io/badge/TOOL-PYTHON_3-059669?style=for-the-badge&logo=python)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — How do you find the attacker's source IP?</strong></summary>

<br>

Use `sort` and `uniq -c` on the source IP column to count requests by IP address. Legitimate internal infrastructure will generate many requests. Look for an IP that queries domains that don't match the internal naming conventions — or one that generates a disproportionate volume of unusual subdomain lookups.

</details>

<details>
<summary><strong>▶ Hint 2 — What does DNS exfiltration look like in a log?</strong></summary>

<br>

The attacker's queries will target a domain they control (not an internal domain). The subdomain portion — the part before the main domain — will look like random characters rather than a meaningful hostname. That "random" string is actually encoded data. Look for queries like `aGVsbG8=.evil-domain.com`.

</details>

<details>
<summary><strong>▶ Hint 3 — How do you reconstruct the payload?</strong></summary>

<br>

The data is split across multiple DNS queries in order. Extract the subdomain from each exfiltration query, concatenate them in sequence, then decode the full combined string. In Python: `import base64; base64.b64decode("combined_string")`. The result is the flag.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the decoded content of the concatenated DNS subdomain payloads.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
