#!/usr/bin/env python3
"""Build the Logic Pro Crash Course eBook.

Reads the JSON content files in ./content and emits a single self-contained
HTML file in ./dist with fonts inlined as data URIs. The same file is used
for the clickable on-screen edition and, via Chromium's print pipeline, for
the printable PDF.

The design follows the dannny mcccarthy rates document (brand.py): Figtree,
black grounds alternating with paper, sentence-case display type on tight
negative tracking, small spaced uppercase kickers, 16px rounded hairline cards,
pill controls and the signature. Tokens and fonts come from brand.py so the
book, the library and the sales page cannot drift apart.
"""

import base64
import html
import json
import pathlib
import re

import brand

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
FONTS = ROOT / "fonts"
FIGURES = ROOT / "figures"
DIST = ROOT / "dist"

# --------------------------------------------------------------------------
# Design tokens — mirrored from dannnymcccarthy.com/css/style.css :root
# --------------------------------------------------------------------------
TOKENS = {**brand.TOKENS, "body_dim": brand.TOKENS["muted_dark"]}


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
    # block, not swap: the PDF is printed once, and it must be printed in Figtree
    return brand.font_faces(display="block")


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
    stats = [(str(total_tips), "Tricks", "Each one cites its source"),
             (str(section_count), "Sections", "Setup to mixing to export"),
             ("100%", "Clickable", "Every entry is a link")]
    chips = "".join(
        f'<div class="stat"><span class="stat-l">{esc(l)}</span><span class="stat-n">{n}</span>'
        f'<span class="stat-t">{esc(d)}</span></div>'
        for n, l, d in stats
    )
    return f"""
<section class="page hero" id="cover">
  {brand.signature_img("sig reveal")}
  <p class="hero-kicker reveal">{esc(front["edition"])} &middot; An eBook by dannny mcccarthy</p>
  <h1 class="hero-title reveal d1">Logic Pro Crash Course.</h1>
  <p class="hero-tag reveal d2">{esc(front["subtitle"].format(n=total_tips))}. {esc(front["tagline"])}</p>
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
    bits.append(f'<p class="lead sec-lede">{esc(section["intro"])}</p>')
    if section.get("intro_src"):
        bits.append(sources_html(section["intro_src"], cls="doc-src"))
    bits.append(f'<p class="sec-count">{tips_total} tricks</p>')
    bits.append("</header>")

    bits.append('<div class="sec-body">')

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
  <footer class="book-foot reveal d3">
    <div>Logic Pro Crash Course &middot; {esc(front_edition())}<br>dannny mcccarthy &middot; dannnymcccarthy.com</div>
    {brand.signature_img("mark-sig")}
  </footer>
  <p class="legal">{esc(legal_notice())}</p>
</section>"""


def front_edition():
    return json.loads((CONTENT / "00-front.json").read_text())["edition"]


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------
def stylesheet():
    return font_faces() + brand.root_vars() + BOOK_CSS


# The rates document's system, extended to a book. Surfaces alternate the way
# the rates page does: black for the cover, contents, section openers and the
# close; paper for everything you read. Type is sentence case on tight negative
# tracking; the only uppercase is the small spaced kicker and label.
BOOK_CSS = """
:root{--rail-w:15rem;--body-dim:var(--muted-dark);--line:var(--line-dark);--read:760px}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--black);color:var(--white);font-family:var(--font);font-weight:400;
  line-height:1.5;-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit;text-decoration:none}
a:focus-visible{outline:2px solid currentColor;outline-offset:4px}
h1,h2,h3,h4{margin:0;font-weight:700}

/* surfaces */
.hero,.toc,.sec-head,.outro{background:var(--black);color:var(--white);--body-dim:var(--muted-dark);--line:var(--line-dark)}
.doc,.sec-body{background:var(--paper);color:var(--ink);--body-dim:var(--muted-light);--line:var(--line-light)}

/* type */
.display-xl{font-size:clamp(38px,8.4vw,120px);line-height:.94;letter-spacing:-.048em;text-wrap:balance}
.display-l{font-size:clamp(34px,6.4vw,96px);line-height:.96;letter-spacing:-.048em;text-wrap:balance}
.eyebrow,.hero-kicker{margin:0;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.24em;color:var(--kicker)}
.doc .eyebrow,.sec-body .eyebrow{color:var(--muted-light)}
.sub{margin:0;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;line-height:1.3}
.lead{margin:0;max-width:60ch;font-size:clamp(15px,1.3vw,19px);line-height:1.6;color:var(--body-dim)}

/* shell */
.shell{display:grid;grid-template-columns:var(--rail-w) minmax(0,1fr)}
.book{min-width:0}
.page{padding:clamp(64px,12vh,150px) var(--pad)}
.page>*{max-width:var(--maxw);margin-left:auto;margin-right:auto}

/* rail */
.rail{position:sticky;top:0;align-self:start;height:100vh;background:var(--black);color:var(--white);
  border-right:1px solid var(--line-dark);padding:26px 0 16px;display:flex;flex-direction:column;gap:18px}
.rail-brand{margin:0 22px;font-weight:700;font-size:17px;letter-spacing:-.03em;line-height:1.05}
.rail-scroll{overflow-y:auto;display:flex;flex-direction:column;padding-bottom:24px}
.rail-link{position:relative;display:flex;gap:.7rem;align-items:baseline;padding:.42rem 22px;font-size:13px;
  line-height:1.35;color:var(--muted-dark);opacity:.6;transition:opacity .25s var(--ease),transform .25s var(--ease)}
.rail-link:hover{opacity:1;transform:translateX(4px)}
.rail-link.is-active{opacity:1}
.rail-link.is-active::before{content:"";position:absolute;left:0;top:.55rem;width:2px;height:1.1em;background:var(--white)}
.rail-n{font-size:11px;font-weight:600;letter-spacing:.12em;color:var(--kicker);font-variant-numeric:tabular-nums;min-width:1.4rem}

/* signature */
.sig{display:block;width:clamp(150px,16vw,230px);height:auto;margin:0 0 clamp(22px,4vh,40px);filter:invert(1)}
.mark-sig{display:block;width:150px;height:auto;filter:invert(1)}

/* cover */
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center}
.hero>*{width:100%}
.hero-kicker{margin-bottom:clamp(20px,4vh,38px)}
.hero-title{font-size:clamp(44px,8.4vw,140px);line-height:.94;letter-spacing:-.048em;max-width:12ch}
.hero-tag{margin:clamp(30px,5vh,54px) 0 0;max-width:52ch;font-size:clamp(16px,1.6vw,22px);color:var(--muted-dark)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(12px,2vw,26px);margin-top:clamp(40px,7vh,90px)}
.stat{border:1px solid var(--line-dark);border-radius:16px;padding:clamp(20px,2.6vw,34px)}
.stat-l{display:block;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.2em;color:var(--label)}
.stat-n{display:block;margin:14px 0 4px;font-weight:700;font-size:clamp(38px,4.4vw,64px);line-height:1;
  letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stat-t{display:block;font-size:13px;color:var(--label)}

/* contents */
.toc-head{margin-bottom:clamp(34px,6vh,64px)}
.toc-head .display-xl{margin-top:clamp(16px,3vh,30px)}
.toc-list{list-style:none;margin:0;padding:0}
.toc-row{display:flex;align-items:baseline;gap:clamp(14px,2.4vw,34px);padding:clamp(12px,1.6vh,18px) 0;
  border-bottom:1px solid var(--line-dark);transition:transform .3s var(--ease)}
.toc-list li:first-child .toc-row{border-top:1px solid var(--line-dark)}
.toc-row:hover{transform:translateX(8px)}
.toc-n{min-width:2rem;font-size:12px;font-weight:600;letter-spacing:.14em;color:var(--kicker);font-variant-numeric:tabular-nums}
.toc-n-empty{opacity:.4}
.toc-label{flex:1;font-size:clamp(18px,2.2vw,30px);font-weight:700;letter-spacing:-.03em;line-height:1.1}
.toc-go{font-size:13px;color:var(--label);white-space:nowrap;font-variant-numeric:tabular-nums}
.toc-foot{margin:clamp(30px,5vh,54px) 0 0;font-size:13px;color:var(--kicker)}

/* front-matter documents */
.doc-head{padding-bottom:clamp(22px,4vh,40px)}
.doc-head .display-l{margin-top:clamp(16px,3vh,30px)}
.doc-body{display:flex;flex-direction:column;gap:clamp(22px,3.4vh,34px);margin-top:clamp(10px,2vh,20px)}
.rules{margin:0;padding:0;list-style:none}
.rules li{position:relative;padding:14px 0 14px 22px;border-bottom:1px solid var(--line);color:var(--body-dim);
  font-size:15px;line-height:1.6;max-width:72ch}
.rules li:first-child{border-top:1px solid var(--line)}
.rules li::before{content:"";position:absolute;left:0;top:1.45em;width:8px;height:1px;background:currentColor;opacity:.5}
.legend{margin:0;display:flex;flex-direction:column}
.legend-row{display:grid;grid-template-columns:14rem minmax(0,1fr);gap:1.2rem;align-items:baseline;padding:14px 0;border-bottom:1px solid var(--line)}
.legend-row:first-child{border-top:1px solid var(--line)}
.legend-row dt{display:flex;align-items:baseline;gap:1rem}
.legend-sym{font-size:26px;font-weight:500;line-height:1;min-width:2rem}
.legend-name{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em}
.legend-row dd{margin:0;font-size:15px;color:var(--body-dim)}
.cmd-block{display:flex;flex-direction:column;gap:14px}
.cmd-block .sub{padding-bottom:12px;border-bottom:1px solid var(--line)}
.cmd-table{width:100%;border-collapse:collapse}
.cmd-table tr{border-bottom:1px solid var(--line)}
.cmd-table th{text-align:left;padding:10px 20px 10px 0;width:11rem;vertical-align:baseline}
.cmd-table td{padding:10px 0;font-size:15px;color:var(--body-dim);vertical-align:baseline}

/* key caps: solid pill on the surface's opposite colour */
.kbd{display:inline-block;font-family:var(--font);font-weight:600;font-size:11px;letter-spacing:.1em;
  text-transform:uppercase;background:currentColor;border-radius:100px;padding:.34rem .8rem;white-space:nowrap}
.hero .kbd,.toc .kbd,.sec-head .kbd,.outro .kbd{background:var(--white);color:var(--black)}
.doc .kbd,.sec-body .kbd{background:var(--ink);color:var(--white)}
.kbd-phrase,.doc .kbd-phrase,.sec-body .kbd-phrase{background:transparent;color:inherit;border:1px solid var(--line);letter-spacing:.08em}

.callout,.notice{border:1px solid var(--line);border-radius:16px;padding:clamp(22px,3vw,40px)}
.callout h3,.notice h3{margin:0 0 12px;font-size:clamp(18px,1.8vw,24px);font-weight:700;letter-spacing:-.02em;line-height:1.2}
.callout p,.notice p{margin:0;font-size:15px;line-height:1.65;color:var(--body-dim)}
.notice{margin-top:30px}

/* sections: black opener, paper body */
.section{padding:0}
.section>*{max-width:none}
.sec-head{padding:clamp(80px,14vh,170px) var(--pad) clamp(40px,7vh,80px)}
.sec-head>*{max-width:var(--maxw);margin-left:auto;margin-right:auto}
.sec-head .display-l{margin-top:clamp(16px,3vh,30px);max-width:16ch;margin-left:0}
.sec-lede{margin-top:clamp(20px,3vh,32px)}
.sec-count{display:inline-block;margin:clamp(24px,4vh,40px) 0 0;border:1px solid var(--line-dark);border-radius:100px;padding:8px 20px;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.2em;color:var(--label)}
.sec-body{padding:clamp(50px,9vh,110px) var(--pad) clamp(60px,10vh,120px)}
.sec-body>*{max-width:var(--maxw);margin-left:auto;margin-right:auto}

.group{margin-top:clamp(44px,7vh,90px)}
.group-head{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;padding-bottom:12px;border-bottom:1px solid var(--line)}
.group-path{margin:0;font-size:13px;color:var(--muted-light)}
.group-note{margin:14px 0 0;font-size:14px;color:var(--muted-light)}
.tips{margin-top:clamp(20px,3vh,32px);display:grid;grid-template-columns:repeat(auto-fill,minmax(19rem,1fr));gap:clamp(14px,2vw,26px)}

/* trick card = the rates tier card */
.tip{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:16px;padding:clamp(20px,2.4vw,32px);
  background:var(--paper);color:var(--ink);transition:border-color .35s var(--ease),transform .35s var(--ease)}
.tip:hover{border-color:rgba(0,0,0,.4);transform:translateY(-2px)}
.tip-head{display:flex;align-items:center;flex-wrap:wrap;gap:10px}
.tip-num{font-size:12px;font-weight:500;letter-spacing:.2em;color:var(--muted-light);font-variant-numeric:tabular-nums}
.tip-title{margin:10px 0 0;font-size:clamp(17px,1.5vw,21px);font-weight:700;letter-spacing:-.02em;line-height:1.2}
.tip-body{margin:12px 0 0;font-size:15px;line-height:1.6;color:var(--body-dim);flex:1}
.tip-keys{margin-top:16px}
.tip-fig{margin:14px 0 0}
.tip-fig img{display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}
.sec-body>.notice:first-child{margin-top:0}
.sec-body>.group:first-child,.sec-body>.group-tight:first-child{margin-top:0}
.tip-fig figcaption{margin-top:8px;font-size:12px;line-height:1.5;color:var(--body-dim)}
.tip-src{margin:18px 0 0;padding-top:14px;border-top:1px solid var(--line);font-size:12px;line-height:1.5;color:var(--body-dim)}
.tip-src span,.doc-src span{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;margin-right:6px}
.tip-src a,.doc-src a{color:inherit;text-decoration:underline;text-underline-offset:2px;text-decoration-color:color-mix(in srgb,currentColor 35%,transparent)}
.doc-src{margin:10px 0 0;font-size:12px;line-height:1.55;color:var(--body-dim)}
sup.ref{font-size:10px;font-weight:600;margin-left:3px;color:var(--body-dim)}
.ref-n{font-weight:600;font-size:10px}

/* game changer: the dark tier on a paper page */
.tip-gold{background:var(--black);color:var(--white);border-color:var(--black);--body-dim:var(--muted-dark);--line:var(--line-dark)}
.tip-gold:hover{border-color:var(--black)}
.tip-gold .tip-num{color:var(--label)}
.sec-body .tip-gold .kbd{background:var(--white);color:var(--black)}

.badge{font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;border-radius:100px;padding:4px 11px}
.badge-gold{background:var(--white);color:var(--black)}
.badge-todo,.badge-start{border:1px solid currentColor}
a.gl{color:inherit;text-decoration:underline dotted;text-underline-offset:3px;text-decoration-color:color-mix(in srgb,currentColor 50%,transparent)}
a.gl:hover{text-decoration-style:solid}

/* Start Here */
.steps{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:0}
.step{display:grid;grid-template-columns:52px 1fr;gap:16px;align-items:start;border-top:1px solid var(--line);padding:16px 0;break-inside:avoid}
.step-n{font-size:32px;font-weight:700;letter-spacing:-.048em;line-height:1}
.step h3{font-size:clamp(18px,1.8vw,24px);letter-spacing:-.02em;line-height:1.2}
.step p{margin:6px 0 0;font-size:15px;line-height:1.6;color:var(--body-dim);max-width:64ch}
.step .tip-keys{margin-top:10px}

/* I Want To... */
.goals{columns:2 320px;column-gap:44px;margin-top:10px}
.goal{margin:0 0 28px}
.goal .sub{display:flex;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);padding-bottom:10px;break-after:avoid}
.goal-count{font-weight:500;color:var(--muted-light)}
.goal-list{list-style:none;margin:8px 0 0;padding:0}
.goal-list li{margin:0;break-inside:avoid}
.goal-list a{display:flex;align-items:baseline;gap:10px;padding:3px 0;font-size:14px;line-height:1.45}
.goal-list a:hover{text-decoration:underline}
.gi-n{flex:0 0 auto;font-size:11px;font-weight:600;letter-spacing:.12em;color:var(--muted-light);font-variant-numeric:tabular-nums}
.gi-start{flex:0 0 auto;margin-left:auto;font-size:9px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;
  border:1px solid currentColor;border-radius:100px;padding:2px 8px;opacity:.7}

/* Glossary */
.gloss{margin:10px 0 0;columns:2 320px;column-gap:44px}
.gl-row{break-inside:avoid;border-top:1px solid var(--line);padding:12px 0 14px}
.gl-row dt{font-weight:700;font-size:17px;letter-spacing:-.02em}
.gl-aka{display:block;font-weight:400;font-size:12px;color:var(--muted-light);margin-top:2px;letter-spacing:0}
.gl-row dd{margin:6px 0 0;font-size:14px;line-height:1.6;color:var(--body-dim)}

/* pill */
.pill{display:inline-flex;align-items:center;justify-content:center;padding:20px 46px;border:2px solid currentColor;
  border-radius:100px;font-weight:500;text-transform:uppercase;letter-spacing:.24em;font-size:12px;
  transition:background .35s var(--ease),color .35s var(--ease),transform .35s var(--ease)}
.pill:hover{background:var(--ink);color:var(--white)}
.pill:active{transform:scale(.97)}
.totop{margin:clamp(46px,8vh,90px) 0 0}

/* close */
.outro{min-height:90vh;display:flex;flex-direction:column;justify-content:center}
.outro>*{width:100%}
.outro-lead{margin:clamp(30px,5vh,54px) 0 0;max-width:56ch;font-size:clamp(16px,1.6vw,22px);color:var(--muted-dark)}
.outro-note{margin:16px 0 0;max-width:56ch;font-size:15px;color:var(--label)}
.book-foot{margin-top:clamp(60px,10vh,120px);padding-top:clamp(30px,5vh,50px);border-top:1px solid var(--line-dark);
  display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap;font-size:13px;color:var(--kicker)}
.legal{margin:30px 0 0;max-width:80ch;font-size:11px;line-height:1.6;color:var(--kicker)}

/* reveal: visible by default, hidden only once the script is running */
html.js .reveal{opacity:0;transform:translateY(24px);transition:opacity .9s var(--ease),transform .9s var(--ease)}
html.js .reveal.in{opacity:1;transform:none}
html.js .reveal.d1{transition-delay:.08s}
html.js .reveal.d2{transition-delay:.16s}
html.js .reveal.d3{transition-delay:.24s}
@media (prefers-reduced-motion:reduce){
  html.js .reveal{opacity:1;transform:none;transition:none}
  html{scroll-behavior:auto}
}

@media (max-width:1000px){
  .shell{grid-template-columns:1fr}
  .rail{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line-dark)}
  .rail-scroll{max-height:34vh}
  .legend-row{grid-template-columns:1fr;gap:.4rem}
  .cmd-table th{width:8rem}
  .stats{grid-template-columns:1fr}
}

/* ---------- print ---------- */
@page{size:A4;margin:14mm 13mm}
@page bleed{size:A4;margin:0}
@media print{
  html{scroll-behavior:auto}
  *,*::before,*::after{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important}
  .reveal{opacity:1 !important;transform:none !important}
  .rail,.totop{display:none !important}
  .shell{display:block}
  html,body{background:#fff}
  body{font-size:10pt;color:var(--ink)}
  .doc,.sec-body{background:#fff}
  .tip{background:#fff}
  .tip-gold{background:var(--black)}
  .sec-count{align-self:flex-start}
  .doc,.sec-body{--body-dim:#444}
  .tip-gold{--body-dim:#d9d8d4}
  .page{break-after:page;padding:0;max-width:none}
  .page:last-child{break-after:auto}

  /* black pages bleed to trim, like the rates document's dark bands */
  .hero,.toc,.outro,.sec-head{page:bleed;min-height:297mm;padding:22mm 18mm;display:flex;flex-direction:column;justify-content:center}
  .toc{justify-content:flex-start;padding-top:18mm}
  .sec-head{justify-content:flex-end;padding-bottom:30mm;break-after:page}
  .sig{width:150px;margin-bottom:12mm}
  .hero-title{font-size:60pt}
  .hero-tag{font-size:14pt}
  .stats{margin-top:14mm;gap:10px;grid-template-columns:repeat(3,1fr)}
  .legend-row{grid-template-columns:12rem minmax(0,1fr)}
  .stat{padding:16px}
  .stat-n{font-size:30pt}
  .toc-head .display-xl{font-size:44pt}
  .toc-head{margin-bottom:8mm}
  .toc-row{padding:4.2px 0}
  .toc-label{font-size:12pt}
  .toc-foot{margin-top:6mm;font-size:8pt}
  .toc-n,.toc-go{font-size:7.5pt}
  .sec-head .display-l{font-size:46pt}
  .sec-lede{font-size:13pt !important;max-width:52ch}
  .sec-count{font-size:8pt}
  .sec-head .doc-src{font-size:7pt}
  .outro .display-xl{font-size:48pt}

  .doc{padding:10mm 0}
  .doc-head .display-l{font-size:36pt}
  .sec-body{padding:6mm 0 10mm}
  .sec-body .lead,.doc .lead{font-size:11pt}
  .notice{margin-top:6mm;padding:5mm}
  .callout{padding:5mm}
  .callout h3,.notice h3{font-size:12pt}
  .callout p,.notice p{font-size:9.5pt}
  .rules li,.legend-row dd,.cmd-table td{font-size:9.5pt}
  .rules li{padding:8px 0 8px 20px}
  .legend-row{padding:8px 0}
  .cmd-table th,.cmd-table td{padding:6px 16px 6px 0}

  /* the group is the grid in print, so a heading always travels with its first row */
  .group{margin-top:6mm;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
  .group-head{grid-column:1/-1;padding-bottom:8px}
  .group-note{grid-column:1/-1;margin:0}
  .tips{display:contents}
  .tip{padding:12px 14px;border-radius:12px;break-inside:avoid}
  .tip:hover{transform:none}
  .tip-num{font-size:7pt}
  .tip-title{margin-top:5px;font-size:11pt}
  .tip-body{margin-top:5px;font-size:8.8pt;line-height:1.5}
  .tip-keys{margin-top:8px}
  .kbd{font-size:7pt}
  .tip-src{margin-top:8px;padding-top:6px;font-size:6.8pt}
  .tip-src span,.doc-src span{font-size:6pt}
  .doc-src{font-size:6.8pt}
  sup.ref,.ref-n{font-size:6pt}
  .badge{font-size:6.5pt;padding:2px 8px}
  .tip-fig figcaption{font-size:8pt}
  .step{padding:9px 0}
  .step-n{font-size:20pt}
  .step h3{font-size:12pt}
  .step p,.gl-row dd{font-size:9pt}
  .goal-list a{font-size:8.3pt;padding:1.5px 0}
  .gl-row dt{font-size:10.5pt}
  .book-foot{font-size:8pt}
  .mark-sig{width:110px}
  .legal{font-size:7pt}
  .group-head,.doc-head{break-after:avoid}
  .callout,.notice,.legend-row,.cmd-block{break-inside:avoid}
  .group-tight{break-inside:avoid}
  .callout{break-before:avoid}
}
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
