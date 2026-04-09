# Blackout Protocol

**Category:** Web Exploitation · SQL Injection
**Difficulty:** Medium
**Points:** 500
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

A regional power utility runs a legacy web-based Human Machine Interface (HMI) that authenticates operators before granting access to Grid Zone control data. The system was rushed into production years ago with no security review.

Intelligence suggests the login mechanism has a critical vulnerability. A successful attacker could bypass authentication entirely and reach the classified dashboard where the system flag is stored.

Your mission: access the dashboard without valid credentials.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the class of vulnerability present in the login form |
| 2 | Identify the specific technique used to bypass authentication |
| 3 | Retrieve the flag from the dashboard |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

You will be presented with a login page. No credentials are provided — you are not supposed to know the password. Your job is to get in anyway.

**Interact with:**
- The login form (username and password fields)
- The dashboard (accessible after a successful bypass)

---

## Tools That May Help

- A web browser with developer tools
- [Burp Suite](https://portswigger.net/burp) — intercept and modify HTTP requests
- Basic knowledge of SQL query structure

---

## Things to Think About

- What happens when user input is inserted directly into a database query?
- Which field is the most useful to manipulate and why?
- SQL has special characters that change how a query is interpreted — what are they?
- SQL also has a way to comment out the rest of a line — look that up if you don't know it

---

## Flag Format

```
CTF{...}
```

Submit the flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
