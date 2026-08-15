# Logic Pro Crash Course — eBook

A full-colour, clickable eBook of **361 Logic Pro tricks** across **19 sections**, built from
structured content files so the text and the design can be changed independently.

## Output

| File | What it is |
| --- | --- |
| `dist/logic-pro-crash-course.html` | The clickable edition. Self-contained — fonts are inlined as data URIs, no network needed. Open it in any browser. |
| `dist/logic-pro-crash-course.pdf` | The printable edition. A4, 94 pages, full-bleed black poster pages, paper body pages. |

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

- `00-front.json` — How to Use This Book, Key Legend, The Basic Key Commands
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
| `path` | Menu path for the group (optional) — renders as an outlined pill |
| `notice` | Section-level warning banner (optional) |

Trick numbers are assigned automatically in reading order, so inserting a trick
renumbers everything after it without any manual work.

## Design

The book follows the **dannnymcccarthy.com** design system. Token values in `build.py`
are lifted from that site's `css/style.css` `:root`, so the two stay in step — change
them there, change them here.

| Token | Value | Used for |
| --- | --- | --- |
| `--black` | `#000` | Poster pages: cover, contents, section openers, outro |
| `--paper` | `#fdfdfd` | Body pages in print |
| `--ink` | `#0a0a0a` | Text on paper, inverted cards |
| `--body-dim` | `#d5d4cf` | Muted body copy on dark surfaces |
| `--glass` | `#171922` | Liquid-glass card body |
| `--line-dark` / `--line-light` | `rgba(255,255,255,.18)` / `rgba(0,0,0,.14)` | Hairline rules |

Type is **Poppins** at 400/500/600/700, subset to latin and inlined as base64 woff2 in
`fonts/`. Display headings are 700, uppercase, on tight negative tracking (`-.03em`);
micro-labels are 500/600 uppercase on wide tracking (`.14em`–`.24em`); body copy is 400
at `line-height: 1.7`. Cards carry the site's liquid-glass rim — a 1px gradient frame over
a `#171922` body, with a specular highlight that sweeps the rim on hover.

Two behaviours are ported directly from the site: the `.reveal` fade-up
(`translateY(30px)`, `.9s`, staggered `.d1`/`.d2`/`.d3`) and its IntersectionObserver.
Unlike the site, `.reveal` here only hides content once the script confirms it is running
(`html.js`), so a file opened from disk with JS blocked still renders in full.

**Screen is dark, print inverts.** Poster pages stay black and bleed to trim; body pages
flip to paper so a 94-page book is actually printable. The inversion flips the `--body-dim`
token on the paper surfaces rather than re-listing selectors, so nothing gets missed.

## Known gap

**Section 19 (Logic Pro 12 Update)** ships as an upgrade playbook plus six template cards
marked `ADD YOUR NOTES`. The playbook content is evergreen and correct; the six feature
cards are deliberately unfilled because version-specific claims should come from the
release notes of the exact build you are running. Fill them in and rebuild.
