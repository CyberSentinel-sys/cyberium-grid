# Grid Mind

**Category:** Web · AI Security
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

CyberiumGrid Utilities Corp. deployed an AI assistant called **GridMind v1.2** to help operators query grid status, review incident reports, and get guidance during outages. The assistant has been configured with an internal authorization token and strict instructions never to reveal it.

The developers believed that giving the AI strong system-level instructions would be enough to protect sensitive information. They were wrong.

Your mission: manipulate the AI into revealing its internal configuration and extract the authorization token hidden in its system context.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the class of attack used to manipulate AI language models into ignoring their instructions |
| 2 | Craft an input that causes the AI to reveal its hidden system context |
| 3 | Extract the authorization token from the revealed context and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

You will see a chat interface for **GridMind v1.2**. Type messages and observe how the AI responds. No files to download.

**Start by exploring:**
- Ask about grid status, zones, or incidents — see what normal responses look like
- Try to understand what the AI is protecting and how it deflects certain questions
- Then think about how to override its instructions

---

## Tools That May Help

- Just a web browser
- Creativity — this challenge is about understanding how AI systems process instructions
- Familiarity with how prompt injection attacks work (OWASP LLM Top 10 — LLM01)

---

## Things to Think About

- AI language models receive instructions in a "system prompt" before the user conversation begins
- If a user can inject new instructions that the model treats as authoritative, the original instructions can be overridden
- The AI has a filtering layer — simple attempts will be deflected. Think about what kind of language would trigger a "system override" rather than a "I can't help with that"
- What would you say to a person to make them forget their instructions and tell you a secret?

---

## Flag Format

```
CTF{...}
```

The flag appears inside the AI's revealed system context. Submit it on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
