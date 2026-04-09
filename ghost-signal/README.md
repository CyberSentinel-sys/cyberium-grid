<div align="center">

# ░▒▓ GHOST SIGNAL ▓▒░

<br>

[![Category](https://img.shields.io/badge/CATEGORY-OSINT-d97706?style=for-the-badge&logo=openstreetmap)](https://cyberium.io)
[![Technique](https://img.shields.io/badge/TECHNIQUE-METADATA_ANALYSIS-d97706?style=for-the-badge&logo=openstreetmap)](https://cyberium.io)
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
> OSINT unit has been tracking a threat actor operating under the alias **z3r0grid** —
> a known adversary with a history of targeting critical infrastructure operators.
>
> Activity spiked three days ago. A public paste appeared on a grid operator
> paste service, attributed to z3r0grid's active profile. The paste itself was
> unremarkable — noise, misdirection. But the profile had a linked avatar.
>
> A PNG image. Small. Innocuous. The kind of thing you'd scroll past.
>
> Image files are not just pixels. Every PNG can carry embedded metadata —
> invisible fields that record authorship, software, timestamps, and arbitrary
> key-value pairs that image viewers never display. The PNG standard supports
> a chunk type called `tEXt` that allows any string to be stored alongside the image.
>
> z3r0grid embedded something in that avatar. A token. A signal.
> Something that was never meant for anyone who wasn't looking at the right layer.
>
> **Download the image. Look past the pixels. Extract the signal.**

---

## ╔══════════════════════════════╗
## ║   MISSION OBJECTIVES         ║
## ╚══════════════════════════════╝

| MISSION | OBJECTIVE | STATUS |
|:-------:|-----------|:------:|
| `M-01` | Identify the **tool or technique** used to extract hidden metadata from the image | `LOCKED` |
| `M-02` | Identify the **metadata field name** containing the hidden token | `LOCKED` |
| `M-03` | Extract the token value and **retrieve the flag** | `LOCKED` |

> Complete missions in sequence. Mission 3 cannot be submitted without completing 1 and 2.

---

## ╔══════════════════════════════╗
## ║   RECOVERED EVIDENCE         ║
## ╚══════════════════════════════╝

**Launch your instance on [Cyberium Arena](https://cyberium.io).**

Navigate the challenge interface — explore the profile page before downloading.
Then retrieve the avatar image:

```
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ FILE            │ DESCRIPTION                                                │
├─────────────────┼────────────────────────────────────────────────────────────┤
│ avatar.png      │ Profile avatar of threat actor z3r0grid                   │
│                 │ PNG with tEXt metadata chunk containing a hidden token     │
└─────────────────┴────────────────────────────────────────────────────────────┘
```

> **Tip:** The challenge interface has multiple pages. Explore before you download —
> the full picture matters for OSINT methodology.

---

## ╔══════════════════════════════╗
## ║   RECOMMENDED TOOLKIT        ║
## ╚══════════════════════════════╝

```
▸  exiftool — reads all metadata fields embedded in image files
▸  strings — extracts printable text from any binary
▸  xxd — raw hex view for manual inspection
▸  Python Pillow — from PIL import Image; img.info — reads PNG tEXt chunks
```

[![OSINT](https://img.shields.io/badge/TOOL-EXIFTOOL-d97706?style=for-the-badge&logo=openstreetmap)](https://cyberium.io)
[![Python](https://img.shields.io/badge/TOOL-PYTHON_PILLOW-d97706?style=for-the-badge&logo=python)](https://cyberium.io)

---

## ╔══════════════════════════════╗
## ║   ANALYST NOTES              ║
## ╚══════════════════════════════╝

<details>
<summary><strong>▶ Hint 1 — What tool do you use?</strong></summary>

<br>

`exiftool` is the standard tool for reading all metadata embedded in image files. Run `exiftool avatar.png` and it will display every field — standard EXIF fields and any custom PNG `tEXt` chunks stored in the file.

</details>

<details>
<summary><strong>▶ Hint 2 — What are you looking for in the output?</strong></summary>

<br>

The `exiftool` output will list many fields. Look for a field with an unusual or custom name — not a standard EXIF field like `Width`, `Height`, or `Color Type`. A custom key-value pair in a PNG `tEXt` chunk will appear with whatever key name the creator chose.

</details>

<details>
<summary><strong>▶ Hint 3 — Alternative approach</strong></summary>

<br>

`strings avatar.png` will dump all readable text from the file, including the content of any `tEXt` chunks. Scan the output for anything resembling the flag format `CTF{...}` or a suspicious field name followed by a token value.

</details>

---

## ╔══════════════════════════════╗
## ║   FLAG FORMAT                ║
## ╚══════════════════════════════╝

<div align="center">

```
CTF{...}
```

*The flag is the token value stored in the PNG tEXt metadata chunk.*
*Submit under Mission 3 on the Cyberium Arena platform.*

</div>

---

<div align="center">

*Part of the Cyberium Hack the Grid challenge collection*
<br>
[← Back to Hub](../README.md)

**CyberSentinel-sys · 2026**

</div>
