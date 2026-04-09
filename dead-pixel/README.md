<div align="center">

# ░▒▓ DEAD PIXEL ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-MISC_·_STEGANOGRAPHY-7c3aed?style=for-the-badge&logo=python)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-PNG_ANALYSIS-7c3aed?style=for-the-badge&logo=python)](https://cyberium.io)
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
> A grid status map image was recovered from an operator workstation
> during a forensic sweep following an insider threat investigation.
>
> The image displays what looks like routine telemetry — zone statuses
> across the CyberiumGrid network. Green lights. Normal readings. Nothing alarming.
>
> But the file is too large. Not by much — a few hundred bytes more than the
> image dimensions and color depth should ever produce. Enough to notice,
> if you're looking at the right numbers.
>
> Image viewers don't show you everything. They decode the pixel data and stop.
> What comes after the last pixel — after the official end of the image format —
> is invisible to any viewer. It's not rendered. It's not displayed. It's just... there.
>
> Someone used this image as a dead drop. The flag was smuggled out in the silence
> after the picture ends. **Find what's hiding past the edge of the image.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **tool or technique** used to find non-visual data in the image file | `LOCKED` |
| `M-02` | Identify **where in the PNG file structure** the hidden data begins | `LOCKED` |
| `M-03` | Extract the hidden data and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Download the image file from the challenge interface:

```
┌─────────────────────┬──────────────────────────────────────────────────────┐
│ FILE                │ DESCRIPTION                                          │
├─────────────────────┼──────────────────────────────────────────────────────┤
│ grid_status.png     │ Grid telemetry status map — PNG format               │
│                     │ File size is larger than image content warrants      │
└─────────────────────┴──────────────────────────────────────────────────────┘
```

> **Do not open this in an image viewer.** What you see visually is not the whole story.
> Analyze the raw binary contents of the file. The answer is not in the pixels.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  strings — extract all printable text from any binary file
▸  xxd / hexedit — view raw bytes in hexadecimal
▸  binwalk — detect and extract embedded/appended data
▸  exiftool — read image metadata and file properties
▸  HxD / wxHexEditor — graphical hex editors
```

[![Tools](https://img.shields.io/badge/TOOL-STRINGS_+_BINWALK-7c3aed?style=for-the-badge&logo=python)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — What is the PNG file structure?</strong></summary>

<br>

PNG files follow a strict chunk-based structure. Every valid PNG file ends with a specific chunk called `IEND`. Any bytes that appear in the file after the `IEND` chunk are outside the official image format — invisible to image viewers, but readable by anyone inspecting the raw file.

</details>

<details>
<summary><strong>▶ Hint 2 — What's the fastest way to find hidden text?</strong></summary>

<br>

The `strings` command extracts all sequences of printable ASCII characters from a binary file. Run `strings grid_status.png` and look for anything that resembles the flag format `CTF{...}`. You don't need to understand the PNG format to find readable text appended to it.

</details>

<details>
<summary><strong>▶ Hint 3 — For deeper analysis</strong></summary>

<br>

`binwalk grid_status.png` will detect the PNG structure and flag any data that exists beyond the expected file boundary. `xxd grid_status.png | tail -40` lets you inspect the raw bytes at the end of the file directly.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is appended to the PNG file after the IEND chunk.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
