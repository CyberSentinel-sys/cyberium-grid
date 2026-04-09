# Log Sweep

**Category:** Forensics · Log Analysis
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

Following a security alert at CyberiumGrid Utilities Corp., the SOC team pulled the web server access logs from the affected node. At first glance, the log looks routine — hundreds of internal API calls from known grid systems.

But something is hiding in plain sight. One entry doesn't belong. And it's carrying a payload that was never meant to be seen.

Your mission: find the anomaly, decode the hidden data, and extract the flag.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the IP address of the suspicious/attacker request |
| 2 | Identify the field within that request that contains encoded data, and the encoding scheme used |
| 3 | Decode the value and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download the log file from the challenge interface:

| File | Description |
|------|-------------|
| `grid_access.log` | Web server access log — Apache Combined Log Format |

Open the file and read through it. The log is approximately 100 lines. Most traffic is legitimate — look for what doesn't fit.

---

## Tools That May Help

- Any plain text editor
- Command line tools: `grep`, `sort`, `uniq`, `cat`
- A base64 decoder (`base64 -d` on Linux, or any online tool)
- Spreadsheet or log viewer for easier reading

---

## Things to Think About

- Legitimate internal traffic comes from known internal IP ranges — anything outside that range is suspicious
- Web server logs record many fields per request: IP, timestamp, path, status code, size, referrer, and **User-Agent**
- Attackers sometimes hide data in fields that are logged but rarely inspected
- Once you spot the suspicious entry, look carefully at every field — one of them contains encoded data

---

## Flag Format

```
CTF{...}
```

Submit the decoded flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
