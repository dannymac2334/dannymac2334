# Logic Pro Crash Course — eBook

A full-colour, clickable eBook of **361 Logic Pro tricks** across **19 sections**, built from
structured content files so the text and the design can be changed independently.

## Output

| File | What it is |
| --- | --- |
| `dist/logic-pro-crash-course.html` | The clickable edition. Self-contained — fonts are inlined as data URIs, no network needed. Open it in any browser. |
| `dist/logic-pro-crash-course.pdf` | The printable edition. A4, 74 pages, full-bleed poster covers. |

## Building

```bash
python3 validate.py                  # check accuracy and structure first
python3 build.py                     # writes dist/logic-pro-crash-course.html

# PDF (any Chromium build works; this is the path in the dev container)
/opt/pw-browsers/chromium-1194/chrome-linux/chrome \
  --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=dist/logic-pro-crash-course.pdf \
  --virtual-time-budget=25000 dist/logic-pro-crash-course.html
```

`build.py` prints a per-section trick count on every run, so a content change that drops
the total below 350 is visible immediately.

## Editing the content

All copy lives in `content/` — the build script never contains prose.

- `00-front.json` — About Me, Introduction, Key Legend, The Basic Key Commands
- `01.json` … `19.json` — one file per section

A section looks like this:

```json
{
  "number": 9,
  "title": "Marquee Tool Tricks",
  "intro": "…",
  "groups": [
    {
      "heading": "The essentials",
      "path": "Logic Pro > Settings > Audio",
      "tips": [
        { "t": "Title", "d": "Body copy.", "k": "⌘ + drag", "b": "GOLDEN NUGGET" }
      ]
    }
  ]
}
```

| Key | Meaning |
| --- | --- |
| `t` | Trick title |
| `d` | Body copy |
| `k` | Key command (optional) — renders as a keycap chip |
| `b` | Badge (optional) — `GOLDEN NUGGET` or `ADD YOUR NOTES` |
| `path` | Menu path for the group (optional) — renders as a purple pill |
| `notice` | Section-level warning banner (optional) |

Trick numbers are assigned automatically in reading order, so inserting a trick
renumbers everything after it without any manual work.

## Design

| Token | Value | Used for |
| --- | --- | --- |
| Chartreuse | `#D8DC30` | Page ground, poster pages, section banners |
| Ink | `#141410` | Body text, keycaps, outro page |
| Electric purple | `#6B18D4` | Kickers, trick numbers, decorative marks |
| Signal orange | `#E2622B` | Contents frame, Golden Nugget cards |
| Paper | `#FBFBF2` | Section and document page grounds |

Type is **Anton** for display and **Inter** for body, both subset to latin and inlined
as base64 woff2 in `fonts/`. The starbursts and squiggles in the margins are generated
in Python (`starburst()` / `squiggle()`) rather than hand-authored path data.

The design commits to a single visual world, so it does not swap for dark mode — every
colour, including `body`'s background, is painted explicitly so the page holds on any host.

## Accuracy

`validate.py` runs four checks and exits non-zero on failure, so it drops straight into CI:

1. **Structural** — malformed JSON, missing fields, trick count below the 350 the cover promises.
2. **Duplication** — the same trick written twice under a different section.
3. **Contradiction** — one key command claimed for two different actions, which means at
   least one of them is wrong.
4. **Provenance** — any key command not present in the verified registry at the top of
   `validate.py`, so a newly invented shortcut cannot reach the PDF unnoticed.

The registry splits into `CONFIRMED` (checked against Apple's Logic Pro User Guide or two
or more independent references) and `STANDARD` (long-standing factory defaults). Current
state: 361 tricks, 58 distinct key commands, 0 failures, 0 warnings.

Where a command could not be confirmed, the book gives the **exact command name and menu
path** instead of asserting a keystroke — always correct, and still usable, since the reader
can search that name in Key Commands (⌥K). Prefer that pattern over guessing when you add
tricks.

## Known gap

**Section 19 (Logic Pro 12 Update)** ships as an upgrade playbook plus six template cards
marked `ADD YOUR NOTES`. The playbook content is evergreen and correct; the six feature
cards are deliberately unfilled because version-specific claims should come from the
release notes of the exact build you are running. Fill them in and rebuild.
