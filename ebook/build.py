#!/usr/bin/env python3
"""Build the Logic Pro Crash Course eBook.

Reads the JSON content files in ./content and emits a single self-contained
HTML file in ./dist with fonts inlined as data URIs. The same file is used
for the clickable on-screen edition and, via Chromium's print pipeline, for
the printable PDF.

The design follows the dannnymcccarthy.com system: Poppins, a black ground
alternating with paper, uppercase display type on tight negative tracking,
pill controls, hairline rules and the site's liquid-glass rim on cards.
Token values are lifted from that site's css/style.css so the two stay in
step — change them there, change them here.
"""

import base64
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
FONTS = ROOT / "fonts"
FIGURES = ROOT / "figures"
DIST = ROOT / "dist"

# --------------------------------------------------------------------------
# Design tokens — mirrored from dannnymcccarthy.com/css/style.css :root
# --------------------------------------------------------------------------
TOKENS = {
    "paper": "#fdfdfd",
    "black": "#000",
    "ink": "#0a0a0a",
    "white": "#fff",
    "muted_dark": "#f5f4f1",
    "muted_light": "#666",
    "body_dim": "#d5d4cf",
    "glass": "#171922",
    "line_dark": "rgba(255,255,255,.18)",
    "line_light": "rgba(0,0,0,.14)",
    "ease": "cubic-bezier(.22,.61,.36,1)",
}

WEIGHTS = ["400", "500", "600", "700"]

# The badge that marks a standout trick. Any other badge string renders in the
# quieter outlined style, so adding a second badge type needs no code change.
HIGHLIGHT_BADGE = "GAME CHANGER"


# Apple's guidelines for third-party publications require a non-affiliation
# disclaimer and a trademark attribution in the credits of the publication and
# its related materials. Wording follows Apple's own template:
# https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html
APPLE_MARKS = ["Apple", "Logic Pro", "Mac", "macOS", "MainStage", "iPad", "Finder"]


def legal_notice(title="Logic Pro Crash Course"):
    marks = ", ".join(APPLE_MARKS[:-1]) + " and " + APPLE_MARKS[-1]
    return (f"{title} is an independent publication and has not been authorized, sponsored, "
            f"or otherwise approved by Apple Inc. {marks} are trademarks of Apple Inc., registered "
            f"in the U.S. and other countries and regions. Cited sources belong to their "
            f"publishers and are linked so you can check them.")


def esc(text):
    return html.escape(str(text), quote=False)


def font_faces():
    out = []
    for w in WEIGHTS:
        data = base64.b64encode((FONTS / f"poppins-{w}.woff2").read_bytes()).decode()
        out.append(
            "@font-face{font-family:'Poppins';font-style:normal;font-weight:%s;"
            "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');}"
            % (w, data)
        )
    return "".join(out)


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
def load():
    front = json.loads((CONTENT / "00-front.json").read_text())
    sections = sorted(
        (json.loads(p.read_text()) for p in CONTENT.glob("[0-9][0-9].json")),
        key=lambda s: s["number"],
    )
    return front, sections


def load_extras():
    """Beginner layer: glossary entries and goal definitions, if present."""
    g = CONTENT / "glossary.json"
    goals = CONTENT / "goals.json"
    return (json.loads(g.read_text()) if g.exists() else [],
            json.loads(goals.read_text()) if goals.exists() else [])


def term_pattern(glossary):
    """One regex over every glossary term and alias, longest first."""
    names = []
    for e in glossary:
        if e.get("nolink"):
            continue          # too common to link everywhere; still searchable and in the glossary
        for n in [e["term"], *e.get("aka", [])]:
            names.append((n, e["id"]))
    names.sort(key=lambda x: -len(x[0]))
    if not names:
        return None, {}
    lookup = {n.lower(): i for n, i in names}
    rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(n) for n, _ in names) + r")(?![\w-])", re.I)
    return rx, lookup


def link_terms(escaped, rx, lookup, render, limit=3):
    """Link the first occurrence of each glossary term in already-escaped text."""
    if rx is None:
        return escaped
    used, count = set(), [0]

    def sub(m):
        gid = lookup.get(m.group(1).lower())
        if gid is None or gid in used or count[0] >= limit:
            return m.group(0)
        used.add(gid); count[0] += 1
        return render(m.group(0), gid)
    # never touch text inside an existing tag
    parts = re.split(r"(<[^>]+>)", escaped)
    return "".join(pt if pt.startswith("<") else rx.sub(sub, pt) for pt in parts)


GLOSS = {"rx": None, "lookup": {}}   # filled in main()


def count_tips(sections):
    return sum(len(g["tips"]) for s in sections for g in s["groups"])


def slug(section):
    base = re.sub(r"[^a-z0-9]+", "-", section["title"].lower()).strip("-")
    return f"s{section['number']:02d}-{base}"


def keycap(keys):
    raw = str(keys)
    phrase = any(w in raw.lower() for w in ("to assign", "drag", "click", "–"))
    cls = "kbd kbd-phrase" if phrase else "kbd"
    return f'<span class="{cls}">{esc(raw)}</span>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def tip_html(tip, index):
    badge = tip.get("b", "")
    classes = ["tip", "reveal"]
    if badge == HIGHLIGHT_BADGE:
        classes.append("tip-gold")
    elif badge:
        classes.append("tip-todo")

    bits = [f'<article class="{" ".join(classes)}" id="t-{index}">']
    bits.append('<div class="tip-head">')
    bits.append(f'<span class="tip-num">{index:03d}</span>')
    if tip.get("lvl") == 1:
        bits.append('<span class="badge badge-start">Start here</span>')
    if badge:
        cls = "badge badge-gold" if badge == HIGHLIGHT_BADGE else "badge badge-todo"
        bits.append(f'<span class="{cls}">{esc(badge)}</span>')
    bits.append("</div>")
    bits.append(f'<h4 class="tip-title">{esc(tip["t"])}</h4>')
    body = link_terms(esc(tip["d"]), GLOSS["rx"], GLOSS["lookup"],
                      lambda txt, gid: f'<a class="gl" href="#g-{gid}">{txt}</a>')
    bits.append(f'<p class="tip-body">{body}</p>')
    if tip.get("img"):
        bits.append(figure_html(tip["img"], tip.get("caption", "")))
    if tip.get("k"):
        bits.append(f'<div class="tip-keys">{keycap(tip["k"])}</div>')
    if tip.get("src"):
        bits.append(sources_html(tip["src"]))
    bits.append("</article>")
    return "".join(bits)


def sources_html(sources, cls="tip-src"):
    """The citation line under a trick.

    Every factual trick carries the source it was checked against, so a reader
    can confirm it themselves. Links stay live in the PDF.
    """
    links = " · ".join(
        f'<a href="{html.escape(s["url"], quote=True)}">{esc(s["label"])}</a>'
        for s in sources
    )
    return f'<p class="{cls}"><span>Source</span> {links}</p>'


def numbered_refs(items):
    """Footnote-style citations for a list of rows that each carry sources.

    Returns (marks, html): marks[i] is the superscript for item i, and html is
    one numbered source list for the whole block, each source listed once.
    """
    order, marks = [], []
    for srcs in items:
        nums = []
        for s in srcs or []:
            if s["url"] not in [o["url"] for o in order]:
                order.append(s)
            nums.append(1 + [o["url"] for o in order].index(s["url"]))
        marks.append(f'<sup class="ref">{",".join(map(str, sorted(set(nums))))}</sup>' if nums else "")
    if not order:
        return marks, ""
    links = " · ".join(
        f'<span class="ref-n">{i}</span>&nbsp;<a href="{html.escape(s["url"], quote=True)}">{esc(s["label"])}</a>'
        for i, s in enumerate(order, 1))
    return marks, f'<p class="doc-src"><span>Sources</span> {links}</p>'


def figure_html(name, caption=""):
    """Inline a screenshot from figures/ as a data URI.

    The book has to stay self-contained — it is read as a single file with no
    server behind it — so images are embedded rather than linked, the same way
    the fonts are. A missing file is a hard error: a book that silently ships a
    broken image is worse than a build that stops.
    """
    path = FIGURES / name
    if not path.exists():
        raise SystemExit(
            f"figure not found: {path}\n"
            f"Tips reference screenshots by filename; put it in {FIGURES}/ or "
            f"remove the 'img' field from the trick."
        )
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(path.suffix.lstrip(".").lower())
    if mime is None:
        raise SystemExit(f"unsupported image type for {path.name} (use png, jpg or webp)")
    b64 = base64.b64encode(path.read_bytes()).decode()
    cap = f'<figcaption>{esc(caption)}</figcaption>' if caption else ""
    alt = esc(caption or name)
    return (f'<figure class="tip-fig"><img src="data:{mime};base64,{b64}" alt="{alt}">'
            f"{cap}</figure>")


def build_cover(front, total_tips, section_count):
    stats = [(str(total_tips), "Tricks"), (str(section_count), "Sections"), ("100%", "Clickable")]
    chips = "".join(
        f'<div class="stat"><span class="stat-n">{n}</span>'
        f'<span class="stat-l">{esc(l)}</span></div>'
        for n, l in stats
    )
    return f"""
<section class="page hero" id="cover">
  <p class="hero-kicker reveal">{esc(front["edition"])}</p>
  <h1 class="hero-title reveal d1">Logic&nbsp;Pro<br/>Crash&nbsp;Course</h1>
  <p class="hero-sub reveal d2">{esc(front["subtitle"].format(n=total_tips))}</p>
  <p class="hero-tag reveal d2">{esc(front["tagline"])}</p>
  <div class="stats reveal d3">{chips}</div>
</section>"""


def build_toc(front, sections):
    rows = []
    # Front matter is deliberately unnumbered — only the 19 sections carry numbers,
    # so the numbering means something rather than just decorating every row.
    def front_row(page):
        return (f'<li><a class="toc-row" href="#{page["id"]}">'
                f'<span class="toc-n toc-n-empty" aria-hidden="true">&mdash;</span>'
                f'<span class="toc-label">{esc(page["label"])}</span>'
                f'<span class="toc-go">Open</span></a></li>')
    for page in front["pages"]:
        if not page.get("back"):
            rows.append(front_row(page))
    for s in sections:
        tips = sum(len(g["tips"]) for g in s["groups"])
        rows.append(
            f'<li><a class="toc-row" href="#{slug(s)}">'
            f'<span class="toc-n">{s["number"]:02d}</span>'
            f'<span class="toc-label">{esc(s["title"])}</span>'
            f'<span class="toc-go">{tips} tricks</span></a></li>'
        )
    rows += [front_row(p) for p in front["pages"] if p.get("back")]
    return f"""
<section class="page toc" id="contents">
  <header class="toc-head">
    <p class="eyebrow reveal">Logic Pro Crash Course</p>
    <h2 class="display-xl reveal d1">Contents.</h2>
  </header>
  <nav aria-label="Table of contents">
    <ol class="toc-list reveal d2">{"".join(rows)}</ol>
  </nav>
  <p class="toc-foot reveal d3">Every entry is a link. Click it and you are there.</p>
</section>"""


def build_front_page(page):
    bits = [f'<section class="page doc" id="{page["id"]}">']
    bits.append('<header class="doc-head">')
    bits.append(f'<p class="eyebrow reveal">{esc(page["kicker"])}</p>')
    bits.append(f'<h2 class="display-l reveal d1">{esc(page["title"])}</h2>')
    bits.append("</header>")
    bits.append('<div class="doc-body">')

    for para in page.get("body", []):
        bits.append(f'<p class="lead reveal">{esc(para)}</p>')

    if page.get("steps"):
        bits.append('<ol class="steps">')
        for n, st in enumerate(page["steps"], 1):
            key = f'<div class="tip-keys">{keycap(st["key"])}</div>' if st.get("key") else ""
            body = link_terms(esc(st["body"]), GLOSS["rx"], GLOSS["lookup"],
                              lambda txt, gid: f'<a class="gl" href="#g-{gid}">{txt}</a>')
            bits.append(f'<li class="step reveal"><span class="step-n">{n}</span><div>'
                        f'<h3>{esc(st["title"])}</h3><p>{body}</p>{key}'
                        + (sources_html(st["src"], cls="doc-src") if st.get("src") else "")
                        + "</div></li>")
        bits.append("</ol>")

    if page.get("generated") == "goals":
        bits.append(GENERATED.get("goals", ""))
    if page.get("generated") == "glossary":
        bits.append(GENERATED.get("glossary", ""))

    if page.get("list"):
        bits.append('<ul class="rules reveal">')
        for item in page["list"]:
            bits.append(f"<li>{esc(item)}</li>")
        bits.append("</ul>")

    if page.get("keys"):
        marks, refs = numbered_refs([k.get("src") for k in page["keys"]])
        bits.append('<dl class="legend reveal">')
        for k, mark in zip(page["keys"], marks):
            bits.append(
                f'<div class="legend-row"><dt><span class="legend-sym">{esc(k["sym"])}</span>'
                f'<span class="legend-name">{esc(k["name"])}</span></dt>'
                f'<dd>{esc(k["note"])}{mark}</dd></div>'
            )
        bits.append("</dl>")
        bits.append(refs)
        if page.get("keys_src"):
            bits.append(sources_html(page["keys_src"], cls="doc-src"))

    for table in page.get("tables", []):
        bits.append('<div class="cmd-block reveal">')
        bits.append(f'<h3 class="sub">{esc(table["heading"])}</h3>')
        bits.append('<table class="cmd-table"><tbody>')
        marks, refs = numbered_refs([row[2] if len(row) > 2 else table.get("src") for row in table["rows"]])
        for (key, desc, *_), mark in zip(table["rows"], marks):
            bits.append(
                f'<tr><th scope="row"><span class="kbd">{esc(key)}</span></th>'
                f"<td>{esc(desc)}{mark}</td></tr>"
            )
        bits.append("</tbody></table>")
        bits.append(refs)
        bits.append("</div>")

    if page.get("callout"):
        c = page["callout"]
        bits.append(
            f'<aside class="callout reveal"><h3>{esc(c["title"])}</h3>'
            f'<p>{esc(c["text"])}</p>'
            + (sources_html(c["src"], cls="doc-src") if c.get("src") else "")
            + "</aside>"
        )

    bits.append("</div>")
    bits.append(top_link())
    bits.append("</section>")
    return "".join(bits)


GENERATED = {}


def build_goal_index(goals, sections):
    """"I want to…" — every goal, and the numbered tricks that achieve it."""
    by_goal = {g["id"]: [] for g in goals}
    n = 0
    for sec in sections:
        for grp in sec["groups"]:
            for t in grp["tips"]:
                n += 1
                for gid in t.get("goals", []):
                    if gid in by_goal:
                        by_goal[gid].append((n, t))
    out = ['<div class="goals">']
    for g in goals:
        items = sorted(by_goal[g["id"]], key=lambda x: (x[1].get("lvl", 2), x[0]))
        if not items:
            continue
        lis = "".join(
            f'<li><a href="#t-{num}"><span class="gi-n">{num:03d}</span>{esc(t["t"])}'
            + ('<span class="gi-start">Start here</span>' if t.get("lvl") == 1 else "")
            + "</a></li>" for num, t in items)
        out.append(f'<div class="goal reveal"><h3 class="sub">{esc(g["label"])}'
                   f'<span class="goal-count">{len(items)}</span></h3><ol class="goal-list">{lis}</ol></div>')
    out.append("</div>")
    return "".join(out)


def build_glossary(glossary):
    out = ['<dl class="gloss">']
    for e in sorted(glossary, key=lambda e: e["term"].lower()):
        aka = f'<span class="gl-aka">also: {esc(", ".join(e["aka"]))}</span>' if e.get("aka") else ""
        out.append(f'<div class="gl-row" id="g-{e["id"]}"><dt>{esc(e["term"])}{aka}</dt>'
                   f'<dd>{esc(e["def"])}' + (sources_html(e["src"], cls="doc-src") if e.get("src") else "")
                   + "</dd></div>")
    out.append("</dl>")
    return "".join(out)


def top_link():
    return '<p class="totop"><a class="pill" href="#contents">Back to contents</a></p>'


def build_section(section, counter_start):
    tips_total = sum(len(g["tips"]) for g in section["groups"])
    bits = [f'<section class="page section" id="{slug(section)}">']

    bits.append('<header class="sec-head">')
    bits.append(f'<p class="eyebrow">Section {section["number"]:02d}</p>')
    bits.append(f'<h2 class="display-l">{esc(section["title"])}.</h2>')
    bits.append(f'<p class="sec-count">{tips_total} tricks</p>')
    bits.append("</header>")

    bits.append('<div class="sec-body">')
    bits.append(f'<p class="lead reveal">{esc(section["intro"])}</p>')
    if section.get("intro_src"):
        bits.append(sources_html(section["intro_src"], cls="doc-src reveal"))

    if section.get("notice"):
        n = section["notice"]
        bits.append(
            f'<aside class="notice reveal"><h3>{esc(n["title"])}</h3>'
            f'<p>{esc(n["text"])}</p>'
            + (sources_html(n["src"], cls="doc-src") if n.get("src") else "")
            + "</aside>"
        )

    i = counter_start
    last = len(section["groups"]) - 1
    for gi, group in enumerate(section["groups"]):
        # Only a SMALL closing group is kept whole: that is the one case where a
        # split strands a card or two on an otherwise empty page. Everything else
        # splits freely.
        #
        # Retuned after the verification pass cut the book from 364 tricks to 265.
        # The old rule also pinned any group of four or fewer, which was harmless
        # when groups were large but pins two thirds of them at this size — each
        # one demanding a fresh page. Measured over the current content:
        #
        #   closing<=7 or any<=4 (old)   86pp   5 holes   1 stranded
        #   closing<=7 only              85pp   4 holes   1 stranded
        #   closing<=4 only              84pp   1 hole    1 stranded   <- this
        #   never                        84pp   1 hole    2 stranded
        #
        # Re-run /tmp/tune2.py after any large content change; the right threshold
        # is a function of group size, so it moves when the content does.
        tight = " group-tight" if (gi == last and len(group["tips"]) <= 4) else ""
        bits.append(f'<div class="group{tight}">')
        bits.append('<div class="group-head reveal">')
        bits.append(f'<h3 class="sub">{esc(group["heading"])}</h3>')
        if group.get("path"):
            bits.append(f'<p class="group-path">{esc(group["path"])}</p>')
        bits.append("</div>")
        if group.get("note"):
            bits.append(f'<p class="group-note reveal">{esc(group["note"])}</p>')
        bits.append('<div class="tips">')
        for tip in group["tips"]:
            bits.append(tip_html(tip, i))
            i += 1
        bits.append("</div></div>")

    bits.append(top_link())
    bits.append("</div>")
    bits.append("</section>")
    return "".join(bits), i


def build_rail(front, sections):
    items = ['<a class="rail-link" href="#contents">Contents</a>']
    for page in front["pages"]:
        if not page.get("back"):
            items.append(f'<a class="rail-link" href="#{page["id"]}">{esc(page["label"])}</a>')
    for s in sections:
        items.append(
            f'<a class="rail-link rail-sec" href="#{slug(s)}">'
            f'<span class="rail-n">{s["number"]:02d}</span>'
            f'<span>{esc(s["title"])}</span></a>'
        )
    for page in front["pages"]:
        if page.get("back"):
            items.append(f'<a class="rail-link" href="#{page["id"]}">{esc(page["label"])}</a>')
    return (
        '<nav class="rail" aria-label="Sections">'
        '<a class="rail-brand" href="#cover">Logic Pro<br/>Crash Course</a>'
        '<div class="rail-scroll">' + "".join(items) + "</div></nav>"
    )


def build_outro(total_tips):
    return f"""
<section class="page outro" id="end">
  <h2 class="display-xl reveal">That&rsquo;s the {total_tips}.</h2>
  <p class="outro-lead reveal d1">Now close the book and go and finish the song. The tricks are
  only worth something once they are muscle memory, and muscle memory only comes from sessions.</p>
  <p class="outro-note reveal d2">Come back whenever you get stuck. Every section is one click
  away from every page — that is the entire point of it.</p>
  <p class="eyebrow outro-mark reveal d3">Logic Pro Crash Course</p>
  <p class="legal">{esc(legal_notice())}</p>
</section>"""


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------
def stylesheet():
    t = TOKENS
    return f"""
{font_faces()}

:root {{
  --paper: {t['paper']};
  --black: {t['black']};
  --ink: {t['ink']};
  --white: {t['white']};
  --muted-dark: {t['muted_dark']};
  --muted-light: {t['muted_light']};
  --body-dim: {t['body_dim']};
  --glass: {t['glass']};
  --line-dark: {t['line_dark']};
  --line-light: {t['line_light']};
  --font: 'Poppins', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --ease: {t['ease']};
  --pad: clamp(20px, 5.5vw, 90px);
  --maxw: 1100px;
  --rail-w: 16rem;
}}

* {{ box-sizing: border-box; }}

html {{ scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }}

body {{
  margin: 0;
  background: var(--black);
  color: var(--white);
  font-family: var(--font);
  font-weight: 400;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  overflow-x: clip;
}}

a {{ color: inherit; text-decoration: none; }}
a:focus-visible {{ outline: 2px solid currentColor; outline-offset: 4px; }}

h1, h2, h3, h4 {{ margin: 0; font-weight: 700; letter-spacing: -.03em; line-height: .98; }}

/* ---------- type scale ---------- */
.display-xl {{
  font-size: clamp(38px, 8.4vw, 118px);
  text-transform: uppercase;
  letter-spacing: -.005em;
  line-height: .94;
  text-wrap: balance;
}}
.display-l {{
  font-size: clamp(32px, 6.4vw, 84px);
  text-transform: uppercase;
  letter-spacing: -.01em;
  line-height: .94;
  text-wrap: balance;
}}
.eyebrow {{
  margin: 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .24em;
  font-size: 11px;
  opacity: .55;
}}
.sub {{
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .06em;
  line-height: 1.2;
  font-size: clamp(15px, 1.5vw, 19px);
  margin: 0;
}}
.lead {{
  font-size: clamp(16px, 1.25vw, 19px);
  line-height: 1.7;
  color: var(--body-dim);
  margin: 0;
  max-width: 68ch;
}}

/* ---------- shell ---------- */
.shell {{ display: grid; grid-template-columns: var(--rail-w) minmax(0, 1fr); }}
.book {{ min-width: 0; }}
.page {{ padding: clamp(64px, 12vh, 130px) var(--pad); }}
.page > * {{ max-width: var(--maxw); margin-left: auto; margin-right: auto; }}

/* ---------- rail ---------- */
.rail {{
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  background: var(--black);
  border-right: 1px solid var(--line-dark);
  padding: 26px 0 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}}
.rail-brand {{
  margin: 0 24px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -.02em;
  line-height: 1;
  font-size: 15px;
}}
.rail-scroll {{ overflow-y: auto; display: flex; flex-direction: column; padding-bottom: 24px; }}
.rail-link {{
  display: flex;
  gap: .7rem;
  align-items: baseline;
  padding: .44rem 24px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .1em;
  line-height: 1.35;
  color: var(--muted-dark);
  opacity: .6;
  transition: opacity .25s var(--ease), transform .25s var(--ease);
}}
.rail-link:hover {{ opacity: 1; transform: translateX(5px); }}
.rail-link.is-active {{ opacity: 1; }}
.rail-link.is-active::before {{
  content: "";
  position: absolute;
  left: 0;
  width: 2px;
  height: 1.1em;
  background: var(--white);
}}
.rail-link {{ position: relative; }}
.rail-n {{ font-variant-numeric: tabular-nums; opacity: .55; min-width: 1.4rem; }}

/* ---------- cover ---------- */
.hero {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 22px;
}}
.hero-kicker {{
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: .42em;
  font-size: 12px;
  color: var(--muted-dark);
  opacity: .8;
  padding-left: .42em;
  margin: 0;
}}
.hero-title {{
  font-size: clamp(42px, 8.6vw, 118px);
  text-transform: uppercase;
  letter-spacing: -.035em;
  line-height: .88;
  margin: 0;
}}
.hero-sub {{
  margin: 6px 0 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .04em;
  font-size: clamp(15px, 2.2vw, 26px);
}}
.hero-tag {{
  margin: 0;
  text-transform: uppercase;
  letter-spacing: .045em;
  font-size: clamp(12px, 1.15vw, 15px);
  color: var(--muted-dark);
  opacity: .7;
}}
.stats {{ display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; margin-top: 18px; }}
.stat {{
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 14px 30px;
  min-width: 128px;
}}
.stat-n {{
  display: block;
  font-weight: 700;
  font-size: 26px;
  line-height: 1;
  letter-spacing: -.03em;
  font-variant-numeric: tabular-nums;
}}
.stat-l {{
  display: block;
  margin-top: 6px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: .2em;
  text-transform: uppercase;
  opacity: .6;
}}

/* ---------- contents ---------- */
.toc-head {{ margin-bottom: clamp(34px, 6vh, 64px); }}
.toc-head .display-xl {{ margin-top: 14px; }}
.toc-list {{ list-style: none; margin: 0; padding: 0; }}
.toc-row {{
  display: flex;
  align-items: baseline;
  gap: clamp(14px, 2.4vw, 34px);
  padding: clamp(13px, 1.7vh, 20px) 0;
  border-bottom: 1px solid var(--line-dark);
  transition: transform .3s var(--ease), opacity .3s var(--ease);
}}
.toc-list li:first-child .toc-row {{ border-top: 1px solid var(--line-dark); }}
.toc-row:hover {{ transform: translateX(8px); }}
.toc-n {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .14em;
  opacity: .45;
  font-variant-numeric: tabular-nums;
  min-width: 2rem;
}}
.toc-label {{
  flex: 1;
  font-size: clamp(17px, 2.2vw, 30px);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -.02em;
  line-height: 1.05;
}}
.toc-n-empty {{ opacity: .22; }}
.toc-go {{
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .16em;
  opacity: .5;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}}
.toc-foot {{
  margin: clamp(30px, 5vh, 54px) 0 0;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .16em;
  opacity: .45;
}}

/* ---------- front-matter documents ---------- */
.doc-head {{ padding-bottom: clamp(22px, 4vh, 40px); border-bottom: 1px solid var(--line-dark); }}
.doc-head .display-l {{ margin-top: 14px; }}
.doc-body {{ display: flex; flex-direction: column; gap: clamp(22px, 3.4vh, 34px); margin-top: clamp(30px, 5vh, 52px); }}

.rules {{ margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; }}
.rules li {{
  padding: 15px 0 15px 30px;
  border-bottom: 1px solid var(--line-dark);
  position: relative;
  color: var(--body-dim);
  font-size: clamp(14px, 1.1vw, 16px);
  line-height: 1.6;
  max-width: 72ch;
}}
.rules li:first-child {{ border-top: 1px solid var(--line-dark); }}
.rules li::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 1.5em;
  width: 14px;
  height: 1px;
  background: currentColor;
  opacity: .5;
}}

.legend {{ margin: 0; display: flex; flex-direction: column; }}
.legend-row {{
  display: grid;
  grid-template-columns: 14rem minmax(0, 1fr);
  gap: 1.2rem;
  align-items: baseline;
  padding: 15px 0;
  border-bottom: 1px solid var(--line-dark);
}}
.legend-row:first-child {{ border-top: 1px solid var(--line-dark); }}
.legend-row dt {{ display: flex; align-items: baseline; gap: 1rem; }}
.legend-sym {{ font-size: 26px; font-weight: 500; line-height: 1; min-width: 2rem; }}
.legend-name {{
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .16em;
}}
.legend-row dd {{ margin: 0; font-size: 14px; color: var(--body-dim); }}

.cmd-block {{ display: flex; flex-direction: column; gap: 14px; }}
.cmd-table {{ width: 100%; border-collapse: collapse; }}
.cmd-table tr {{ border-bottom: 1px solid var(--line-dark); }}
.cmd-table tr:first-child {{ border-top: 1px solid var(--line-dark); }}
.cmd-table th {{ text-align: left; padding: 11px 20px 11px 0; width: 11rem; vertical-align: baseline; }}
.cmd-table td {{
  padding: 11px 0;
  font-size: 14px;
  color: var(--body-dim);
  vertical-align: baseline;
}}

.kbd {{
  display: inline-block;
  font-family: var(--font);
  font-weight: 600;
  font-size: 11px;
  letter-spacing: .1em;
  text-transform: uppercase;
  background: var(--white);
  color: var(--black);
  border-radius: 100px;
  padding: .34rem .8rem;
  white-space: nowrap;
}}
.kbd-phrase {{
  background: transparent;
  color: var(--white);
  border: 1px solid var(--line-dark);
  letter-spacing: .08em;
}}

.callout {{
  border: 1px solid var(--line-dark);
  border-radius: 16px;
  padding: clamp(22px, 3vw, 34px);
}}
.callout h3 {{
  margin: 0 0 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .06em;
  font-size: clamp(15px, 1.5vw, 19px);
}}
.callout p {{ margin: 0; font-size: 15px; line-height: 1.7; color: var(--body-dim); }}

/* ---------- sections ---------- */
.section {{ padding: 0; max-width: none; }}
.section > * {{ max-width: none; }}
.sec-head {{
  border-bottom: 1px solid var(--line-dark);
  padding: clamp(80px, 14vh, 150px) var(--pad) clamp(34px, 6vh, 62px);
  text-align: center;
}}
.sec-head .display-l {{ margin: 16px auto 0; max-width: 18ch; }}
.sec-count {{
  margin: 20px 0 0;
  display: inline-block;
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 7px 20px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: .18em;
  text-transform: uppercase;
  opacity: .7;
}}
.sec-body {{
  max-width: var(--maxw);
  margin: 0 auto;
  padding: clamp(40px, 7vh, 78px) var(--pad) clamp(60px, 10vh, 110px);
}}

.notice {{
  margin-top: 30px;
  border: 1px solid var(--line-dark);
  border-radius: 16px;
  padding: clamp(20px, 2.6vw, 30px);
}}
.notice h3 {{
  margin: 0 0 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .06em;
  font-size: 15px;
}}
.notice p {{ margin: 0; font-size: 14px; line-height: 1.7; color: var(--body-dim); }}

.group {{ margin-top: clamp(44px, 7vh, 80px); }}
.group-head {{
  display: flex;
  align-items: baseline;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line-dark);
}}
.group-path {{
  margin: 0;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .14em;
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 5px 14px;
  opacity: .7;
}}
.group-note {{ margin: 16px 0 0; font-size: 13px; color: var(--muted-light); }}

.tips {{
  margin-top: 26px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
  gap: 18px;
}}

/* Liquid glass rim, lifted from the site's card treatment. */
.tip {{
  position: relative;
  border-radius: 16px;
  padding: 1px;
  background:
    linear-gradient(135deg,
      rgba(255,255,255,.9) 0%,
      rgba(255,255,255,.28) 16%,
      rgba(255,255,255,.08) 42%,
      rgba(255,255,255,.08) 60%,
      rgba(255,255,255,.3) 82%,
      rgba(255,255,255,.8) 100%),
    linear-gradient(0deg, var(--glass), var(--glass));
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,.22),
    0 0 0 1px rgba(255,255,255,.1),
    0 20px 44px -24px rgba(0,0,0,.7),
    0 4px 14px -10px rgba(0,0,0,.55);
  transition: box-shadow .5s var(--ease);
}}
.tip::before {{
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(120deg, rgba(255,255,255,0) 38%, rgba(255,255,255,.9) 50%, rgba(255,255,255,0) 62%);
  background-size: 260% 100%;
  background-position: 100% 0;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  opacity: 0;
  transition: opacity .5s var(--ease), background-position .9s var(--ease);
}}
.tip:hover::before {{ opacity: 1; background-position: 0 0; }}
.tip:hover {{
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,.4),
    0 0 0 1px rgba(255,255,255,.2),
    0 0 22px -2px rgba(220,230,255,.32),
    0 20px 44px -22px rgba(0,0,0,.7);
}}
.tip-inner, .tip > * {{ position: relative; z-index: 2; }}
.tip {{ display: flex; flex-direction: column; }}
.tip > .tip-head, .tip > .tip-title, .tip > .tip-body, .tip > .tip-keys {{
  background: var(--glass);
}}
.tip > .tip-head {{
  border-radius: 15px 15px 0 0;
  padding: 20px 22px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}}
.tip > .tip-title {{ padding: 12px 22px 0; }}
.tip > .tip-body {{ padding: 10px 22px 0; flex: 1; }}
.tip > .tip-keys {{ padding: 16px 22px 20px; border-radius: 0 0 15px 15px; }}
.tip-fig {{ margin: 0; padding: 0 22px 18px; background: var(--glass); }}
.tip-fig img {{ display: block; width: 100%; height: auto; border-radius: 8px;
  border: 1px solid var(--line-dark); }}
.tip-fig figcaption {{ margin-top: 8px; font-size: 11px; line-height: 1.5;
  color: var(--body-dim); letter-spacing: .01em; }}
.tip:not(:has(.tip-keys)) > .tip-body {{ padding-bottom: 22px; border-radius: 0 0 15px 15px; }}
.tip > .tip-src {{ background: var(--glass); margin: 0; padding: 12px 22px 18px;
  border-radius: 0 0 15px 15px; font-size: 10.5px; line-height: 1.5; color: var(--body-dim); }}
.tip-src span {{ font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  font-size: 9px; opacity: .7; margin-right: 4px; }}
.tip-src a {{ color: inherit; text-decoration: underline; text-decoration-thickness: 1px;
  text-underline-offset: 2px; text-decoration-color: rgba(255,255,255,.3); }}
.tip:has(.tip-src) > .tip-keys {{ padding-bottom: 0; border-radius: 0; }}
.doc-src {{ margin: 10px 0 0; font-size: 10.5px; line-height: 1.55; color: var(--body-dim); }}
sup.ref {{ font-size: 9px; font-weight: 600; margin-left: 3px; color: var(--body-dim); letter-spacing: .02em; }}
.ref-n {{ font-weight: 600; font-size: 9px; opacity: .8; }}
.doc-src span {{ font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  font-size: 9px; opacity: .7; margin-right: 4px; }}
.doc-src a {{ color: inherit; text-decoration: underline; text-underline-offset: 2px;
  text-decoration-color: rgba(255,255,255,.3); }}
.tip:has(.tip-src):not(:has(.tip-keys)) > .tip-body {{ padding-bottom: 0; border-radius: 0; }}

.tip-num {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .14em;
  opacity: .45;
  font-variant-numeric: tabular-nums;
}}
.tip-title {{
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -.01em;
  line-height: 1.25;
  text-transform: none;
}}
.tip-body {{ margin: 0; font-size: 13.5px; line-height: 1.65; color: var(--body-dim); }}

.badge {{
  font-size: 9px;
  font-weight: 600;
  letter-spacing: .18em;
  text-transform: uppercase;
  border-radius: 100px;
  padding: 4px 11px;
}}
.badge-gold {{ background: var(--white); color: var(--black); }}
.badge-todo {{ border: 1px solid var(--line-dark); color: var(--white); opacity: .8; }}
.badge-start {{ border: 1px solid currentColor; color: var(--body-dim); }}
a.gl {{ color: inherit; text-decoration: underline dotted; text-underline-offset: 3px;
  text-decoration-color: rgba(255,255,255,.45); }}
a.gl:hover {{ text-decoration-style: solid; }}

/* Start Here — numbered first steps */
.steps {{ list-style: none; margin: 20px 0 0; padding: 0; display: grid; gap: 8px; }}
.step {{ display: grid; grid-template-columns: 44px 1fr; gap: 16px; align-items: start;
  border-top: 1px solid var(--line-dark); padding-top: 11px; break-inside: avoid; }}
.step-n {{ font-size: 26px; font-weight: 700; letter-spacing: -.03em; line-height: 1; }}
.step h3 {{ margin: 0; font-size: 17px; font-weight: 600; }}
.step p {{ margin: 4px 0 0; font-size: 14px; line-height: 1.55; color: var(--body-dim); max-width: 64ch; }}
.step .tip-keys {{ padding: 6px 0 0; background: none; }}

/* "I want to…" — goals and the tricks that get you there */
.goals {{ columns: 2 320px; column-gap: 40px; margin-top: 24px; }}
.goal {{ margin: 0 0 26px; }}
.goal .sub {{ break-after: avoid; }}
.goal-list li {{ break-inside: avoid; }}
.goal .sub {{ display: flex; align-items: baseline; gap: 10px; border-bottom: 1px solid var(--line-dark);
  padding-bottom: 8px; }}
.goal-count {{ font-size: 11px; font-weight: 500; letter-spacing: .1em; opacity: .6; }}
.goal-list {{ list-style: none; margin: 8px 0 0; padding: 0; }}
.goal-list li {{ margin: 0; }}
.goal-list a {{ display: flex; align-items: baseline; gap: 10px; padding: 3px 0; color: inherit;
  text-decoration: none; font-size: 13px; line-height: 1.45; }}
.goal-list a:hover {{ text-decoration: underline; }}
.gi-n {{ flex: 0 0 auto; font-size: 10.5px; font-weight: 600; letter-spacing: .1em; opacity: .55;
  font-variant-numeric: tabular-nums; }}
.gi-start {{ flex: 0 0 auto; margin-left: auto; font-size: 8.5px; font-weight: 600; letter-spacing: .16em;
  text-transform: uppercase; border: 1px solid currentColor; border-radius: 100px; padding: 2px 8px; opacity: .7; }}

/* Glossary */
.gloss {{ margin: 24px 0 0; columns: 2 320px; column-gap: 40px; }}
.gl-row {{ break-inside: avoid; border-top: 1px solid var(--line-dark); padding: 12px 0 14px; }}
.gl-row dt {{ font-weight: 600; font-size: 15px; }}
.gl-aka {{ display: block; font-weight: 400; font-size: 11px; opacity: .6; margin-top: 2px; }}
.gl-row dd {{ margin: 6px 0 0; font-size: 13.5px; line-height: 1.6; color: var(--body-dim); }}
.tip-gold {{ box-shadow: inset 0 0 0 1px rgba(255,255,255,.45), 0 0 0 1px rgba(255,255,255,.2), 0 20px 44px -24px rgba(0,0,0,.7); }}

/* ---------- pill ---------- */
.pill {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16px 38px;
  border: 2px solid currentColor;
  border-radius: 100px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .24em;
  font-size: 11px;
  transition: background .35s var(--ease), color .35s var(--ease), transform .35s var(--ease);
}}
.pill:hover {{ background: var(--white); color: var(--black); }}
.pill:active {{ transform: scale(.97); }}
.totop {{ margin: clamp(46px, 8vh, 90px) 0 0; }}

/* ---------- outro ---------- */
.outro {{
  min-height: 88vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 22px;
  border-top: 1px solid var(--line-dark);
}}
.outro-lead {{ margin: 0; max-width: 46ch; font-size: clamp(16px, 1.5vw, 21px); line-height: 1.55; }}
.outro-note {{ margin: 0; max-width: 48ch; font-size: 14px; line-height: 1.7; color: var(--muted-light); }}
.outro-mark {{ margin-top: 26px; }}
.legal {{ margin: 40px 0 0; max-width: 70ch; font-size: 10.5px; line-height: 1.6; color: rgba(255,255,255,.62); }}

/* ---------- reveal (matches the site) ----------
   Content is visible by default and only hidden once the script confirms it
   is running, so the book never renders blank if JS is blocked or fails. */
html.js .reveal {{
  opacity: 0;
  transform: translateY(30px);
  transition: opacity .9s var(--ease), transform .9s var(--ease);
}}
html.js .reveal.in {{ opacity: 1; transform: none; }}
html.js .reveal.d1 {{ transition-delay: .08s; }}
html.js .reveal.d2 {{ transition-delay: .16s; }}
html.js .reveal.d3 {{ transition-delay: .24s; }}

@media (prefers-reduced-motion: reduce) {{
  html.js .reveal {{ opacity: 1; transform: none; transition: none; }}
  html {{ scroll-behavior: auto; }}
  * {{ animation: none !important; }}
}}

/* ---------- responsive ---------- */
@media (max-width: 1000px) {{
  .shell {{ grid-template-columns: 1fr; }}
  .rail {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line-dark); }}
  .rail-scroll {{ max-height: 34vh; }}
  .legend-row {{ grid-template-columns: 1fr; gap: .4rem; }}
  .cmd-table th {{ width: 8rem; }}
}}

/* ---------- print ---------- */
@page {{ size: A4; margin: 14mm 13mm; }}
@page bleed {{ size: A4; margin: 0; }}

@media print {{
  html {{ scroll-behavior: auto; }}
  *, *::before, *::after {{
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  .reveal {{ opacity: 1 !important; transform: none !important; }}
  .rail, .totop {{ display: none !important; }}
  .shell {{ display: block; }}
  /* The page ground must be paper, not the screen's black. Otherwise the space
     left when a section ends mid-page renders as a solid black block rather
     than as the chapter simply being over. Poster pages re-blacken below. */
  body {{ font-size: 10pt; background: var(--paper); color: var(--ink); }}

  .page {{
    break-after: page;
    page-break-after: always;
    padding: 0;
    max-width: none;
  }}
  .page:last-child {{ break-after: auto; page-break-after: auto; }}

  /* Poster pages keep the black ground and bleed to trim. */
  .hero, .toc, .outro {{
    page: bleed;
    background: var(--black);
    color: var(--white);
    min-height: 297mm;
    padding: 20mm 16mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}
  .toc {{ justify-content: flex-start; padding-top: 16mm; }}
  .hero-title {{ font-size: 62pt; }}
  .toc-head .display-xl {{ font-size: 46pt; }}
  .toc-row {{ padding: 6.5px 0; }}
  .toc-label {{ font-size: 13pt; }}
  .toc-n, .toc-go {{ font-size: 7pt; }}

  /* Body pages invert to paper so the book is printable. Flipping the muted
     token on the surface itself re-colours every descendant that uses it,
     rather than listing selectors one at a time and missing some. */
  .doc, .section {{ --body-dim: #3a3a38; }}
  .doc, .section, .sec-body {{ background: var(--paper); color: var(--ink); }}
  .doc, .section {{ padding: 0; }}
  .doc {{ padding: 12mm 0; }}
  .sec-body {{ padding: 10mm 0 12mm; max-width: none; }}
  .doc-head {{ padding-bottom: 6mm; border-color: var(--line-light); }}
  /* Hairlines on paper only — the contents page stays black and keeps its own. */
  .doc .rules li, .doc .legend-row, .doc .cmd-table tr, .sec-body .group-head {{
    border-color: var(--line-light);
  }}
  .doc .callout, .sec-body .notice, .sec-body .group-path {{ border-color: var(--line-light); }}

  /* Section banner stays black — it is the divider that paces the book. */
  .sec-head {{
    page: bleed;
    background: var(--black);
    color: var(--white);
    padding: 34mm 16mm 20mm;
    min-height: 297mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;   /* keep the count pill from stretching to full width */
    break-after: page;
    page-break-after: always;
  }}
  .sec-head .display-l {{ font-size: 40pt; }}

  .kbd {{ background: var(--ink); color: var(--white); }}
  .kbd-phrase {{
    background: transparent;
    color: var(--ink);
    border: 1px solid rgba(0,0,0,.32);
  }}

  /* Tighter vertical rhythm on paper. The screen spacing is generous because
     it scrolls; on a fixed page it wastes rows and strands single cards after
     a break. */
  /* In print the group becomes the grid itself and the cards join it via
     display:contents. The heading is then a grid item spanning both columns,
     so it physically cannot be stranded on its own page when Chromium moves
     or fragments the grid — it travels with the first row of cards. */
  .group {{
    margin-top: 4mm;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }}
  .group-head {{ grid-column: 1 / -1; padding-bottom: 9px; }}
  .group-note {{ grid-column: 1 / -1; margin: 0; }}
  .tips {{ display: contents; }}
  .sec-body .lead {{ font-size: 11pt; }}
  .notice {{ margin-top: 7mm; padding: 5mm; }}

  /* Cards go flat on paper — the glass rim is a screen effect. */
  .tips {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 6mm; }}
  .tip {{
    background: none;
    box-shadow: none;
    border: 1px solid var(--line-light);
    border-radius: 12px;
    padding: 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .tip::before {{ content: none; }}
  .tip > .tip-head, .tip > .tip-title, .tip > .tip-body, .tip > .tip-keys {{ background: none; }}
  .tip > .tip-head {{ padding: 10px 12px 0; }}
  .tip > .tip-title {{ padding: 6px 12px 0; }}
  .tip > .tip-body {{ padding: 5px 12px 0; }}
  .tip > .tip-keys {{ padding: 8px 12px 10px; }}
  .tip-fig {{ padding: 0 12px 10px; background: none;
    break-inside: avoid; page-break-inside: avoid; }}
  .tip-fig img {{ border-color: var(--line-light); }}
  .tip-fig figcaption {{ font-size: 8pt; color: var(--body-dim); }}
  .tip:not(:has(.tip-keys)) > .tip-body {{ padding-bottom: 12px; }}
  .tip > .tip-src {{ background: none; padding: 6px 12px 10px; font-size: 6.8pt; }}
  .doc-src {{ font-size: 6.8pt; }}
  sup.ref, .ref-n {{ font-size: 6pt; }}
  .doc-src a {{ text-decoration-color: rgba(0,0,0,.3); }}
  .tip-src a {{ text-decoration-color: rgba(0,0,0,.3); }}
  .tip:has(.tip-src) > .tip-keys {{ padding-bottom: 0; }}
  .tip:has(.tip-src):not(:has(.tip-keys)) > .tip-body {{ padding-bottom: 0; }}
  /* The inverted card keeps the dark-surface token so its copy stays legible. */
  .tip-gold {{
    --body-dim: #d5d4cf;
    background: var(--ink);
    color: var(--white);
    border-color: var(--ink);
    box-shadow: none;
  }}
  .tip-gold .badge-gold {{ background: var(--white); color: var(--ink); }}
  .tip-gold .kbd {{ background: var(--white); color: var(--ink); }}
  .tip-gold .kbd-phrase {{
    background: transparent;
    color: var(--white);
    border-color: rgba(255,255,255,.45);
  }}
  .badge-todo {{ border-color: var(--line-light); color: inherit; }}
  .badge-start {{ color: inherit; border-color: var(--line-light); }}
  .tip-gold .badge-start {{ color: var(--white); border-color: rgba(255,255,255,.5); }}
  a.gl {{ text-decoration-color: rgba(0,0,0,.35); }}
  .tip-gold a.gl {{ text-decoration-color: rgba(255,255,255,.5); }}
  .step, .goal-list, .goal .sub, .gl-row {{ border-color: var(--line-light); }}
  .step {{ break-inside: avoid; page-break-inside: avoid; }}
  .step p, .gl-row dd {{ font-size: 9pt; }}
  .goal-list a {{ font-size: 8.3pt; padding: 1.5px 0; }}
  .gl-row dt {{ font-size: 10pt; }}

  .group-head, .doc-head {{ break-after: avoid; page-break-after: avoid; }}
  .callout, .notice, .legend-row, .cmd-block {{ break-inside: avoid; page-break-inside: avoid; }}
  /* Keep short groups on one page rather than splitting off a lone card. */
  .group-tight {{ break-inside: avoid; page-break-inside: avoid; }}
  /* A closing callout should never be the only thing on a page. */
  .callout {{ break-before: avoid; page-break-before: avoid; }}
}}
"""


SCRIPT = """
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  // Opt into the hidden-then-reveal state only now that the script is running.
  document.documentElement.classList.add('js');
  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  }

  var links = {};
  Array.prototype.slice.call(document.querySelectorAll('.rail-link')).forEach(function (l) {
    links[l.getAttribute('href').slice(1)] = l;
  });
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  if (!('IntersectionObserver' in window)) return;
  var seen = {};
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { seen[e.target.id] = e.isIntersecting; });
    Object.keys(links).forEach(function (k) { links[k].classList.remove('is-active'); });
    for (var i = 0; i < pages.length; i++) {
      if (seen[pages[i].id] && links[pages[i].id]) {
        links[pages[i].id].classList.add('is-active');
        break;
      }
    }
  }, { rootMargin: '-12% 0px -70% 0px' });
  pages.forEach(function (p) { if (p.id) spy.observe(p); });
})();
"""


def main():
    front, sections = load()
    total = count_tips(sections)

    glossary, goals = load_extras()
    GLOSS["rx"], GLOSS["lookup"] = term_pattern(glossary)
    GENERATED["goals"] = build_goal_index(goals, sections) if goals else ""
    GENERATED["glossary"] = build_glossary(glossary) if glossary else ""

    body = [build_rail(front, sections), '<main class="book">']
    body.append(build_cover(front, total, len(sections)))
    body.append(build_toc(front, sections))
    for page in front["pages"]:
        if not page.get("back"):
            body.append(build_front_page(page))

    counter = 1
    for section in sections:
        chunk, counter = build_section(section, counter)
        body.append(chunk)
    for page in front["pages"]:
        if page.get("back"):
            body.append(build_front_page(page))
    body.append(build_outro(total))
    body.append("</main>")

    doc = (
        "<title>Logic Pro Crash Course</title>\n"
        f"<style>{stylesheet()}</style>\n"
        f'<div class="shell">{"".join(body)}</div>\n'
        f"<script>{SCRIPT}</script>\n"
    )

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course.html"
    out.write_text(doc, encoding="utf-8")
    print(f"Wrote {out}  ({len(doc)/1024:.0f} KB)")
    print(f"Sections: {len(sections)}   Tricks: {total}")


if __name__ == "__main__":
    main()
