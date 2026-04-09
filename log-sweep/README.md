<div align="center">

# ░▒▓ LOG SWEEP ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-FORENSICS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-LOG_ANALYSIS-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)
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
> The SOC team at CyberiumGrid Utilities Corp. triggered an alert at 02:17 local time.
> Something moved through the grid node's web server that shouldn't have.
>
> By 02:19, the access logs had been pulled and handed to forensics.
> At first pass — nothing. Hundreds of internal API calls, all from known grid systems.
> Routine. Procedural. Boring.
>
> At second pass — one entry doesn't match. One IP that has no business being in this log.
> And in that entry, buried in a field that nobody ever reads, something is encoded.
> Something that was never meant to be seen by human eyes.
>
> The attacker used the server's own logging infrastructure to carry a payload out in the open.
> Hidden in plain sight. Right there in the log file that the SOC was already reading.
>
> **Find the anomaly. Identify the field. Decode what's inside.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **IP address** of the suspicious attacker request | `LOCKED` |
| `M-02` | Identify the **log field** containing encoded data and the **encoding scheme** used | `LOCKED` |
| `M-03` | Decode the value and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download the log file from the challenge interface:

```
┌────────────────────┬──────────────────────────────────────────────────────┐
│ FILE               │ DESCRIPTION                                          │
├────────────────────┼──────────────────────────────────────────────────────┤
│ grid_access.log    │ Web server access log — Apache Combined Log Format   │
│                    │ Approximately 100 entries. One is not like the others.│
└────────────────────┴──────────────────────────────────────────────────────┘
```

> Open the file and read it carefully. Most traffic is legitimate — look for what doesn't fit.
> Each log entry records: `IP · Timestamp · Method + Path · Status · Size · Referrer · User-Agent`

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Any plain text editor or terminal pager (less, more)
▸  grep / sort / uniq — filter and isolate anomalies
▸  base64 -d (Linux) or any online decoder
▸  Spreadsheet or log viewer for structured reading
```

[![Forensics](https://img.shields.io/badge/TOOL-GREP_+_BASE64-059669?style=for-the-badge&logo=microsoftazure)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — How do you find the suspicious entry?</strong></summary>

<br>

Legitimate internal traffic originates from known internal IP ranges (e.g., `10.x.x.x`, `192.168.x.x`). Any request from an IP address outside those ranges is suspicious. Look for the outlier.

</details>

<details>
<summary><strong>▶ Hint 2 — Which field contains the encoded payload?</strong></summary>

<br>

Apache Combined Log Format records a `User-Agent` string for every request — the identifier a browser or tool sends with each request. This field is logged but rarely inspected by defenders. It's an ideal hiding place for encoded data. Examine every field of the suspicious entry carefully.

</details>

<details>
<summary><strong>▶ Hint 3 — How do you decode it?</strong></summary>

<br>

Once you've isolated the encoded value from the suspicious field, identify the encoding scheme from its character set and format. Then decode it using `base64 -d` on Linux or an online tool. The decoded output contains the flag.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the decoded content of the hidden field in the anomalous log entry.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
