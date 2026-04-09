# Dead Pixel

**Category:** Misc · Steganography
**Difficulty:** Easy
**Points:** 400
**Platform:** Cyberium Arena — Hack the Grid

---

## Scenario

A grid status map image was recovered from an operator workstation during a forensic investigation. The image appears to show normal telemetry data — zone statuses across the grid network. But the file is larger than it should be for an image of its dimensions.

Something is hiding after the image ends.

Your mission: analyze the image file beyond what any viewer shows you, and extract the concealed data.

---

## Missions

| # | Objective |
|---|-----------|
| 1 | Identify the tool or technique used to find non-visual data appended to the image |
| 2 | Identify where in the file structure the hidden data begins |
| 3 | Extract the hidden data and retrieve the flag |

---

## Getting Started

Launch your challenge instance on **Cyberium Arena**.

Download the image file from the challenge interface:

| File | Description |
|------|-------------|
| `grid_status.png` | Grid telemetry status map (PNG image) |

Do **not** just open it in an image viewer — what you see visually is not the whole file. Analyze the raw file contents.

---

## Tools That May Help

- `strings` — extract printable text from any binary file
- `xxd` or `hexedit` — view raw bytes in hex
- `exiftool` — read image metadata
- `binwalk` — detect and extract embedded data in binary files
- A hex editor (HxD, wxHexEditor)

---

## Things to Think About

- PNG files have a defined structure with a known ending marker — what is the last chunk in a valid PNG?
- Any bytes that appear after the official end of the PNG format are invisible to image viewers
- The `strings` command can reveal readable text hidden anywhere in a binary file
- Look for patterns that resemble the flag format `CTF{...}`

---

## Flag Format

```
CTF{...}
```

Submit the extracted flag on the Cyberium Arena platform under Mission 3.

---

*Part of the Cyberium Hack the Grid challenge collection · [Back to Hub](../README.md)*
