<div align="center">

# ░▒▓ BLACKOUT PROTOCOL ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-WEB_EXPLOITATION-2563eb?style=for-the-badge&logo=firefox)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-SQL_INJECTION-2563eb?style=for-the-badge&logo=firefox)](https://cyberium.io)
[![Difficulty](https://img.shields.io/badge/DIFFICULTY-MEDIUM-d97706?style=for-the-badge)](https://cyberium.io)
[![Points](https://img.shields.io/badge/POINTS-500-6d28d9?style=for-the-badge)](https://cyberium.io)
[![Platform](https://img.shields.io/badge/PLATFORM-CYBERIUM_ARENA-0f172a?style=for-the-badge&logo=docker)](https://cyberium.io)

<br>

</div>

---

## ╔══════════════════════════════╗
## ║   THREAT INTELLIGENCE FILE   ║
## ╚══════════════════════════════╝

> **CLASSIFICATION: RESTRICTED — AUTHORIZED OPERATORS ONLY**
>
> A regional power utility has been running a legacy web-based Human Machine Interface
> for over a decade. The system controls authentication to Grid Zone data — critical
> infrastructure that should never be accessible to unauthorized personnel.
>
> It was rushed into production. Never audited. Never hardened.
>
> Our intelligence unit confirmed what we suspected: the login mechanism is fundamentally
> broken. An attacker who knows the right trick doesn't need a password. They never did.
>
> The classified dashboard is one input field away from being wide open.
> **Your job is to walk through that door.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **vulnerability class** present in the login form | `LOCKED` |
| `M-02` | Identify the **specific bypass technique** used to defeat authentication | `LOCKED` |
| `M-03` | Access the dashboard and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   OPERATIONAL PARAMETERS     ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

You will be presented with a login page. No credentials are provided — you are not supposed to know the password. Your job is to get in anyway.

**Attack surface:**

```
┌─────────────────────────────────┐
│  TARGET: Login Form             │
│  FIELDS: username, password     │
│  BACKEND: Database-authenticated│
│  POST-AUTH: Flag Dashboard      │
└─────────────────────────────────┘
```

No files to download. No wordlists required. This is a logic vulnerability — think, don't brute.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  Web browser with Developer Tools (F12)
▸  Burp Suite — intercept and modify HTTP requests
▸  Basic understanding of SQL query structure
```

[![Burp Suite](https://img.shields.io/badge/TOOL-BURP_SUITE-2563eb?style=for-the-badge&logo=firefox)](https://portswigger.net/burp)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — What class of vulnerability are you looking for?</strong></summary>

<br>

Think about what happens when a web application builds a database query using raw user input — without sanitizing or escaping it first. What can an attacker do with special characters?

</details>

<details>
<summary><strong>▶ Hint 2 — Which field matters most?</strong></summary>

<br>

Not all input fields are equal. Consider how the backend query is likely structured for a login check — and which field gives you the most control over that query's logic.

</details>

<details>
<summary><strong>▶ Hint 3 — How do you make the query always succeed?</strong></summary>

<br>

SQL has a way to make a condition always evaluate to true. It also has a way to ignore everything after a certain point. Combine both ideas.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is displayed on the dashboard after a successful bypass.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
