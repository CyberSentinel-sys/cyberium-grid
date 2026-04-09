# DNS Exfil

**Category:** Forensics · Network Analysis
**Difficulty:** Medium
**Points:** 500
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

The network security team at CyberiumGrid Utilities Corp. noticed unusual outbound traffic during a late-night incident window. A packet capture was taken at the DNS resolver. Most of the queries look normal — routine lookups for internal grid services.

But hidden among hundreds of legitimate DNS queries is an exfiltration channel. An attacker tunneled stolen data out of the network by encoding it into DNS subdomain queries — a technique that bypasses most firewall rules because DNS traffic is rarely blocked.

Your mission: find the exfiltration traffic, identify how the data was encoded, and recover the flag.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the source IP address of the attacker performing the exfiltration |
| 2 | Identify the encoding scheme used to encode data in the DNS subdomain queries |
| 3 | Decode the exfiltrated data and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download the network capture from the challenge interface:

| File | Description |
|------|-------------|
| `capture.log` | DNS query log — tab-separated, approximately 100 entries |

The log is in a human-readable text format. Open it in any text editor or use command-line tools to analyze it.

---

## Tools That May Help

- Any text editor
- `grep`, `sort`, `uniq -c` — filter and count entries by field
- `awk`, `cut` — extract specific columns
- A base64 decoder (`base64 -d` on Linux or any online tool)
- Python for scripting the decode if the data is split across multiple queries

---

## Things to Think About

- Legitimate DNS queries resolve to known internal domains — look for queries to domains that don't belong
- Attackers often encode data in the subdomain portion of DNS queries (the part before the main domain)
- The exfiltration may be spread across multiple queries — you may need to collect and concatenate the encoded pieces
- Once you isolate the suspicious subdomains, identify what encoding was used and decode all of them in order

---

## Flag Format

```
CTF{...}
```

Submit the decoded flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
