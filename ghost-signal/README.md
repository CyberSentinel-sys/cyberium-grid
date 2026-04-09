# Ghost Signal

**Category:** OSINT · Metadata Analysis
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

An OSINT analyst tracking a threat actor known as **z3r0grid** discovered an active profile on a grid operator paste service. The actor posted a public paste and linked to their profile avatar — a small PNG image.

Image files often carry more information than meets the eye. Metadata embedded during creation can reveal system names, authors, tokens, and other artifacts the creator never intended to share publicly.

Your mission: analyze the avatar image metadata and recover the hidden token.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the tool or technique used to extract hidden metadata from the image |
| 2 | Identify the name of the metadata field containing the hidden token |
| 3 | Extract the token value and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Navigate through the challenge interface — you will find a user profile page with a linked avatar. Download the avatar image:

| File | Description |
|------|-------------|
| `avatar.png` | Profile avatar of threat actor z3r0grid |

**Tip:** The challenge interface has multiple pages to explore. Look around before downloading.

---

## Tools That May Help

- `strings` — extract printable strings from any binary
- `exiftool` — read and display all metadata embedded in image files
- `xxd` — view raw hex content
- Python `PIL` / `Pillow` — `from PIL import Image; img.info` to read PNG text chunks

---

## Things to Think About

- PNG files support embedded text metadata through a chunk type called `tEXt` — any key/value pair can be stored there
- `exiftool <filename>` dumps all readable metadata fields — look for unusual or custom field names
- The `strings` command will also reveal any embedded text without needing to understand the file format

---

## Flag Format

```
CTF{...}
```

Submit the extracted flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
