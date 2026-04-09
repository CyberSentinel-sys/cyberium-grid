# Grid Shell

**Category:** Web Exploitation · Command Injection
**Difficulty:** Hard
**Points:** 600
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

CyberiumGrid Utilities Corp. deployed an internal network diagnostic tool that lets operators check connectivity to grid nodes. The interface accepts an IP address and runs a network test against it.

The developers assumed operators would only enter valid IP addresses. They were wrong to assume that.

Your mission: manipulate the diagnostic tool to execute arbitrary commands on the server and read the flag stored in `/flag.txt`.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the class of vulnerability present in the diagnostic tool |
| 2 | Craft an input that executes an additional command alongside the intended network test |
| 3 | Read `/flag.txt` from the server and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

You will see a web interface with a single input field — a network diagnostic tool that accepts a target address. There are no files to download. Everything happens in the browser.

**Try:**
- Submitting a normal IP address first to understand how the tool behaves
- Then think about what the server is likely doing with your input on the backend

---

## Tools That May Help

- A web browser with developer tools
- [Burp Suite](https://portswigger.net/burp) — intercept and modify requests
- Knowledge of Linux shell command chaining operators

---

## Things to Think About

- When a web application passes user input directly to a system command, what can go wrong?
- Linux shells support multiple ways to chain commands together — look up shell metacharacters
- The flag is at a known location: `/flag.txt` — what command reads the contents of a file?
- Think about what the server-side command might look like and where your input ends up inside it

---

## Flag Format

```
CTF{...}
```

Submit the flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
