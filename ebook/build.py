#!/usr/bin/env python3
"""Build the Logic Pro Crash Course eBook.

Reads the JSON content files in ./content and emits a single self-contained
HTML file in ./dist with fonts inlined as data URIs. The same file is used
for the clickable on-screen edition and, via Chromium's print pipeline, for
the printable PDF.
"""

import base64
import html
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
FONTS = ROOT / "fonts"
DIST = ROOT / "dist"

# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------
TOKENS = {
    "chartreuse": "#D8DC30",
    "chartreuse_deep": "#C2C625",
    "ink": "#141410",
    "purple": "#6B18D4",
    "purple_light": "#C9A8F5",
    "orange": "#E2622B",
    "paper": "#FBFBF2",
    "olive": "#6E7040",
}


def esc(text):
    return html.escape(str(text), quote=False)


def font_face(path, family, weight="400", style="normal"):
    data = base64.b64encode((FONTS / path).read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;"
        "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');}"
        % (family, style, weight, data)
    )


# --------------------------------------------------------------------------
# Decorative SVG marks — generated, not hand-authored path data
# --------------------------------------------------------------------------
def starburst(size=120, spokes=24):
    """The radiating purple burst from the cover and page corners."""
    r_out, r_in, c = 58, 30, 60
    lines = []
    for i in range(spokes):
        a = (2 * math.pi / spokes) * i
        x1, y1 = c + r_in * math.cos(a), c + r_in * math.sin(a)
        x2, y2 = c + r_out * math.cos(a), c + r_out * math.sin(a)
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )
    return (
        f'<svg class="burst" width="{size}" height="{size}" viewBox="0 0 120 120" '
        'aria-hidden="true" focusable="false">'
        f'<circle cx="60" cy="60" r="34" fill="{TOKENS["purple"]}"/>'
        f'<g stroke="{TOKENS["purple"]}" stroke-width="5" stroke-linecap="round">'
        + "".join(lines)
        + "</g>"
        f'<circle cx="60" cy="60" r="15" fill="{TOKENS["purple_light"]}"/>'
        "</svg>"
    )


def squiggle(strokes=5, flip=False):
    """The stacked purple brush-dash block from the reference margins."""
    parts = []
    for i in range(strokes):
        y = 14 + i * 34
        parts.append(
            f'<path d="M8 {y + 26} L60 {y} L112 {y + 26}" fill="none" '
            f'stroke="{TOKENS["purple"]}" stroke-width="17" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    transform = ' transform="scale(-1,1) translate(-120,0)"' if flip else ""
    return (
        '<svg class="squiggle" width="120" height="200" viewBox="0 0 120 200" '
        'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        f"<g{transform}>" + "".join(parts) + "</g></svg>"
    )


# --------------------------------------------------------------------------
# Content loading
# --------------------------------------------------------------------------
def load():
    front = json.loads((CONTENT / "00-front.json").read_text())
    sections = []
    for path in sorted(CONTENT.glob("[0-9][0-9].json")):
        sections.append(json.loads(path.read_text()))
    sections.sort(key=lambda s: s["number"])
    return front, sections


def count_tips(sections):
    return sum(len(g["tips"]) for s in sections for g in s["groups"])


def slug(section):
    base = re.sub(r"[^a-z0-9]+", "-", section["title"].lower()).strip("-")
    return f"s{section['number']:02d}-{base}"


# --------------------------------------------------------------------------
# Key command rendering
# --------------------------------------------------------------------------
def keycap(keys):
    """Render a key command string as individual caps, splitting on + and spaces."""
    raw = str(keys)
    if any(w in raw.lower() for w in ("to assign", "drag", "click", "–")):
        # Descriptive commands stay as a single chip so the phrasing survives.
        return f'<span class="kbd kbd-phrase">{esc(raw)}</span>'
    return f'<span class="kbd">{esc(raw)}</span>'


def tip_html(tip, index):
    badge = tip.get("b", "")
    classes = ["tip"]
    if badge == "GOLDEN NUGGET":
        classes.append("tip-gold")
    elif badge == "ADD YOUR NOTES":
        classes.append("tip-todo")

    bits = [f'<article class="{" ".join(classes)}">']
    bits.append('<div class="tip-head">')
    bits.append(f'<span class="tip-num">{index:03d}</span>')
    bits.append(f'<h4 class="tip-title">{esc(tip["t"])}</h4>')
    bits.append("</div>")
    if badge:
        cls = "badge badge-gold" if badge == "GOLDEN NUGGET" else "badge badge-todo"
        bits.append(f'<span class="{cls}">{esc(badge)}</span>')
    bits.append(f'<p class="tip-body">{esc(tip["d"])}</p>')
    if tip.get("k"):
        bits.append(f'<div class="tip-keys">{keycap(tip["k"])}</div>')
    bits.append("</article>")
    return "".join(bits)


# --------------------------------------------------------------------------
# Page builders
# --------------------------------------------------------------------------
def build_cover(front, total_tips, section_count):
    return f"""
<section class="page cover" id="cover">
  <div class="cover-deco cover-deco-tl">{starburst()}</div>
  <div class="cover-deco cover-deco-tr">{starburst()}</div>
  <div class="cover-squig cover-squig-l">{squiggle()}</div>
  <div class="cover-squig cover-squig-r">{squiggle(flip=True)}</div>
  <div class="cover-inner">
    <p class="cover-eyebrow">{esc(front["edition"])}</p>
    <h1 class="cover-title">Logic&nbsp;Pro<br/>Crash&nbsp;Course</h1>
    <div class="cover-rule"></div>
    <p class="cover-sub">{esc(front["subtitle"])}</p>
    <p class="cover-tag">{esc(front["tagline"])}</p>
    <div class="cover-stats">
      <div class="stat"><span class="stat-n">{total_tips}</span><span class="stat-l">Tricks</span></div>
      <div class="stat"><span class="stat-n">{section_count}</span><span class="stat-l">Sections</span></div>
      <div class="stat"><span class="stat-n">100%</span><span class="stat-l">Clickable</span></div>
    </div>
  </div>
  <div class="cover-deco cover-deco-bl">{starburst(64)}</div>
  <div class="cover-deco cover-deco-br">{starburst(64)}</div>
</section>"""


def build_toc(front, sections):
    rows = []
    for page in front["pages"]:
        rows.append(
            f'<li class="toc-row"><a href="#{page["id"]}">'
            f'<span class="toc-label">{esc(page["label"])}</span>'
            '<span class="toc-dots"></span>'
            '<span class="toc-go">Open</span></a></li>'
        )
    for s in sections:
        n = len(s["groups"])
        tips = sum(len(g["tips"]) for g in s["groups"])
        rows.append(
            f'<li class="toc-row"><a href="#{slug(s)}">'
            f'<span class="toc-label"><b>Section {s["number"]}</b> — {esc(s["title"])}</span>'
            '<span class="toc-dots"></span>'
            f'<span class="toc-go">{tips} tricks</span></a></li>'
        )
    return f"""
<section class="page toc" id="contents">
  <div class="toc-deco toc-deco-l">{squiggle()}</div>
  <div class="toc-deco toc-deco-r">{squiggle(flip=True)}</div>
  <header class="toc-head">
    <div class="toc-kicker">{starburst(52)}<span>Logic Pro Crash Course</span>{starburst(52)}</div>
    <h2 class="toc-title">Table of Contents</h2>
  </header>
  <nav class="toc-frame" aria-label="Table of contents">
    <ol class="toc-list">{"".join(rows)}</ol>
  </nav>
  <p class="toc-foot">Every entry is a link. Click it and you are there.</p>
</section>"""


def build_front_page(page):
    bits = [f'<section class="page doc" id="{page["id"]}">']
    bits.append('<header class="doc-head">')
    bits.append(f'<p class="kicker">{esc(page["kicker"])}</p>')
    bits.append(f'<h2 class="doc-title">{esc(page["title"])}</h2>')
    bits.append("</header>")
    bits.append('<div class="doc-body">')

    for para in page.get("body", []):
        bits.append(f"<p>{esc(para)}</p>")

    if page.get("list"):
        bits.append('<ul class="rules">')
        for item in page["list"]:
            bits.append(f"<li>{esc(item)}</li>")
        bits.append("</ul>")

    if page.get("keys"):
        bits.append('<dl class="legend">')
        for k in page["keys"]:
            bits.append(
                f'<div class="legend-row"><dt><span class="legend-sym">{esc(k["sym"])}</span>'
                f'<span class="legend-name">{esc(k["name"])}</span></dt>'
                f'<dd>{esc(k["note"])}</dd></div>'
            )
        bits.append("</dl>")

    for table in page.get("tables", []):
        bits.append('<div class="cmd-block">')
        bits.append(f'<h3 class="cmd-head">{esc(table["heading"])}</h3>')
        bits.append('<table class="cmd-table"><tbody>')
        for key, desc in table["rows"]:
            bits.append(
                f'<tr><th scope="row"><span class="kbd">{esc(key)}</span></th>'
                f"<td>{esc(desc)}</td></tr>"
            )
        bits.append("</tbody></table></div>")

    if page.get("callout"):
        c = page["callout"]
        bits.append(
            f'<aside class="callout"><h3>{esc(c["title"])}</h3><p>{esc(c["text"])}</p></aside>'
        )

    bits.append("</div>")
    bits.append(top_link())
    bits.append("</section>")
    return "".join(bits)


def top_link():
    return '<p class="totop"><a href="#contents">↑ Back to contents</a></p>'


def build_section(section, counter_start):
    tips_total = sum(len(g["tips"]) for g in section["groups"])
    sid = slug(section)
    bits = [f'<section class="page section" id="{sid}">']

    # Section opener banner
    bits.append('<header class="sec-head">')
    bits.append(f'<div class="sec-deco">{squiggle(4)}</div>')
    bits.append('<div class="sec-headtext">')
    bits.append(f'<p class="sec-num">Section {section["number"]}</p>')
    bits.append(f'<h2 class="sec-title">{esc(section["title"])}</h2>')
    bits.append(f'<p class="sec-count">{tips_total} tricks</p>')
    bits.append("</div>")
    bits.append(f'<div class="sec-deco sec-deco-r">{squiggle(4, flip=True)}</div>')
    bits.append("</header>")

    bits.append(f'<p class="sec-intro">{esc(section["intro"])}</p>')

    if section.get("notice"):
        n = section["notice"]
        bits.append(
            f'<aside class="notice"><h3>{esc(n["title"])}</h3><p>{esc(n["text"])}</p></aside>'
        )

    i = counter_start
    for group in section["groups"]:
        bits.append('<div class="group">')
        bits.append('<div class="group-head">')
        bits.append(f'<h3 class="group-title">{esc(group["heading"])}</h3>')
        if group.get("path"):
            bits.append(f'<p class="group-path">{esc(group["path"])}</p>')
        bits.append("</div>")
        if group.get("note"):
            bits.append(f'<p class="group-note">{esc(group["note"])}</p>')
        bits.append('<div class="tips">')
        for tip in group["tips"]:
            bits.append(tip_html(tip, i))
            i += 1
        bits.append("</div></div>")

    bits.append(top_link())
    bits.append("</section>")
    return "".join(bits), i


def build_rail(front, sections):
    items = [
        '<a class="rail-link rail-top" href="#cover">Cover</a>',
        '<a class="rail-link" href="#contents">Contents</a>',
    ]
    for page in front["pages"]:
        items.append(f'<a class="rail-link" href="#{page["id"]}">{esc(page["label"])}</a>')
    for s in sections:
        items.append(
            f'<a class="rail-link rail-sec" href="#{slug(s)}">'
            f'<span class="rail-n">{s["number"]:02d}</span>{esc(s["title"])}</a>'
        )
    return (
        '<nav class="rail" aria-label="Sections">'
        '<p class="rail-head">Jump to</p>'
        '<div class="rail-scroll">' + "".join(items) + "</div></nav>"
    )


def build_outro(total_tips):
    return f"""
<section class="page outro" id="end">
  <div class="cover-deco cover-deco-tl">{starburst(80)}</div>
  <div class="cover-deco cover-deco-br">{starburst(80)}</div>
  <div class="outro-inner">
    <h2 class="outro-title">That&rsquo;s the {total_tips}.</h2>
    <p class="outro-lead">Now close the book and go and finish the song. The tricks are only worth
    something once they are muscle memory, and muscle memory only comes from sessions.</p>
    <p class="outro-note">Come back to this whenever you get stuck. Every section is one click away
    from every page — that is the entire point of it.</p>
    <p class="outro-mark">Logic Pro Crash Course</p>
  </div>
</section>"""


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------
def stylesheet():
    t = TOKENS
    return f"""
{font_face('anton-latin.woff2', 'Anton')}
{font_face('inter-latin.woff2', 'Inter', '100 900')}

:root {{
  --chartreuse: {t['chartreuse']};
  --chartreuse-deep: {t['chartreuse_deep']};
  --ink: {t['ink']};
  --purple: {t['purple']};
  --purple-light: {t['purple_light']};
  --orange: {t['orange']};
  --paper: {t['paper']};
  --olive: {t['olive']};
  --display: 'Anton', 'Haettenschweiler', 'Arial Narrow', sans-serif;
  /* DejaVu carries the Mac modifier glyphs that Inter's latin subset omits. */
  --body: 'Inter', -apple-system, 'Helvetica Neue', 'DejaVu Sans', Arial, sans-serif;
  --page-w: 52rem;
  --rail-w: 15rem;
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: var(--chartreuse);
  color: var(--ink);
  font-family: var(--body);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

a {{ color: inherit; }}
a:focus-visible, .rail-link:focus-visible {{
  outline: 3px solid var(--purple);
  outline-offset: 3px;
}}

/* ---------- Layout shell ---------- */
.shell {{
  display: grid;
  grid-template-columns: var(--rail-w) minmax(0, 1fr);
  gap: 0;
}}
.book {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
  padding: 2.5rem 1.5rem 5rem;
}}
.page {{
  width: 100%;
  max-width: var(--page-w);
  position: relative;
}}

/* ---------- Side rail (screen only) ---------- */
.rail {{
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  background: var(--ink);
  color: var(--paper);
  padding: 1.5rem 0 1rem;
  display: flex;
  flex-direction: column;
  gap: .75rem;
}}
.rail-head {{
  margin: 0 1.25rem;
  font-family: var(--display);
  font-size: .95rem;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--chartreuse);
}}
.rail-scroll {{
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding-bottom: 2rem;
}}
.rail-link {{
  display: flex;
  gap: .6rem;
  align-items: baseline;
  padding: .42rem 1.25rem;
  font-size: .8rem;
  line-height: 1.3;
  text-decoration: none;
  color: #E6E6DA;
  border-left: 3px solid transparent;
}}
.rail-link:hover {{ background: #26261E; color: #fff; border-left-color: var(--orange); }}
.rail-link.is-active {{ background: var(--purple); color: #fff; border-left-color: var(--chartreuse); }}
.rail-top {{ color: var(--chartreuse); }}
.rail-n {{
  font-family: var(--display);
  font-size: .8rem;
  color: var(--chartreuse);
  font-variant-numeric: tabular-nums;
  min-width: 1.4rem;
}}
.rail-link.is-active .rail-n {{ color: #fff; }}

/* ---------- Decorative marks ---------- */
.burst {{ display: block; }}
.squiggle {{ display: block; }}
.cover-deco, .toc-deco, .cover-squig {{
  position: absolute;
  pointer-events: none;
  z-index: 0;
}}
.cover-deco-tl {{ top: 2rem; left: 2rem; }}
.cover-deco-tr {{ top: 2rem; right: 2rem; }}
.cover-deco-bl {{ bottom: 1.75rem; left: 2.25rem; }}
.cover-deco-br {{ bottom: 1.75rem; right: 2.25rem; }}
/* Squiggles bleed off the outer edges so they never sit under running text. */
.cover-squig-l {{ left: -3.5rem; top: 44%; }}
.cover-squig-r {{ right: -3.5rem; top: 20%; }}
.toc-deco-l {{ left: -3.5rem; bottom: 8%; }}
.toc-deco-r {{ right: -3.5rem; top: 30%; }}
.cover-squig .squiggle, .toc-deco .squiggle {{ width: 96px; height: 230px; }}

/* ---------- Cover ---------- */
.cover {{
  background: var(--chartreuse);
  border: 4px solid var(--ink);
  padding: 5.5rem 3rem 5rem;
  overflow: hidden;
  text-align: center;
}}
.cover-inner {{ position: relative; z-index: 2; }}
.cover-eyebrow {{
  margin: 0 0 1.5rem;
  font-family: var(--display);
  font-size: 1rem;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--purple);
}}
.cover-title {{
  margin: 0;
  font-family: var(--display);
  font-size: clamp(3.4rem, 11vw, 6.6rem);
  line-height: .88;
  letter-spacing: .01em;
  text-transform: uppercase;
  text-wrap: balance;
}}
.cover-rule {{
  height: 8px;
  background: var(--orange);
  border-radius: 4px;
  margin: 2rem auto;
  max-width: 22rem;
}}
.cover-sub {{
  margin: 0;
  font-family: var(--display);
  font-size: clamp(1.6rem, 4.5vw, 2.5rem);
  text-transform: uppercase;
  color: var(--purple);
  line-height: 1;
}}
.cover-tag {{
  margin: 1.1rem auto 0;
  max-width: 30rem;
  font-size: 1.05rem;
  font-weight: 500;
}}
.cover-stats {{
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2.75rem;
  flex-wrap: wrap;
}}
.stat {{
  background: var(--ink);
  color: var(--chartreuse);
  border-radius: 14px;
  padding: .85rem 1.4rem;
  min-width: 7.5rem;
}}
.stat-n {{
  display: block;
  font-family: var(--display);
  font-size: 2rem;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}}
.stat-l {{
  display: block;
  font-size: .7rem;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--paper);
  margin-top: .3rem;
}}

/* ---------- Table of contents ---------- */
.toc {{
  background: var(--chartreuse);
  border: 4px solid var(--ink);
  padding: 3rem 2.5rem 3rem;
  overflow: hidden;
}}
.toc-head {{ text-align: center; position: relative; z-index: 2; }}
.toc-kicker {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-family: var(--display);
  font-size: clamp(1.1rem, 3vw, 1.7rem);
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--purple);
}}
.toc-title {{
  margin: .5rem 0 1.75rem;
  font-family: var(--display);
  font-size: clamp(2.6rem, 9vw, 5rem);
  line-height: .9;
  text-transform: uppercase;
}}
.toc-frame {{
  position: relative;
  z-index: 2;
  border: 4px solid var(--orange);
  border-radius: 26px;
  padding: 1.5rem 1.75rem;
  background: rgba(255,255,255,.14);
}}
.toc-list {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}}
.toc-row a {{
  display: flex;
  align-items: baseline;
  gap: .6rem;
  padding: .42rem .25rem;
  text-decoration: none;
  border-radius: 8px;
}}
.toc-row a:hover {{ background: var(--ink); color: var(--chartreuse); }}
.toc-row a:hover .toc-go {{ color: var(--chartreuse); }}
.toc-label {{ text-decoration: underline; text-underline-offset: 3px; font-size: .95rem; }}
.toc-label b {{ font-weight: 700; }}
.toc-dots {{
  flex: 1;
  border-bottom: 2px dotted currentColor;
  opacity: .45;
  transform: translateY(-.28em);
  min-width: 1.5rem;
}}
.toc-go {{
  font-family: var(--display);
  font-size: .82rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--purple);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}}
.toc-foot {{
  position: relative;
  z-index: 2;
  text-align: center;
  margin: 1.5rem 0 0;
  font-size: .85rem;
  font-weight: 600;
  color: var(--olive);
}}

/* ---------- Front-matter document pages ---------- */
.doc {{
  background: var(--paper);
  border: 4px solid var(--ink);
  padding: 2.75rem 2.5rem 2.25rem;
}}
.doc-head {{ border-bottom: 4px solid var(--ink); padding-bottom: 1.25rem; margin-bottom: 1.75rem; }}
.kicker {{
  margin: 0 0 .4rem;
  font-family: var(--display);
  font-size: .85rem;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--purple);
}}
.doc-title {{
  margin: 0;
  font-family: var(--display);
  font-size: clamp(2.2rem, 7vw, 3.6rem);
  line-height: .95;
  text-transform: uppercase;
  text-wrap: balance;
}}
.doc-body {{ display: flex; flex-direction: column; gap: 1.1rem; }}
.doc-body p {{ margin: 0; max-width: 64ch; }}

.rules {{ margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: .7rem; }}
.rules li {{
  position: relative;
  padding-left: 1.6rem;
  max-width: 64ch;
}}
.rules li::before {{
  content: "";
  position: absolute;
  left: 0;
  top: .55em;
  width: .7rem;
  height: .7rem;
  background: var(--orange);
  border-radius: 2px;
}}

.legend {{ margin: 0; display: flex; flex-direction: column; gap: .5rem; }}
.legend-row {{
  display: grid;
  grid-template-columns: 13rem minmax(0, 1fr);
  gap: 1rem;
  align-items: baseline;
  padding: .55rem .75rem;
  background: var(--chartreuse);
  border-radius: 10px;
}}
.legend-row dt {{ display: flex; align-items: baseline; gap: .7rem; }}
.legend-sym {{
  font-family: var(--display);
  font-size: 1.5rem;
  line-height: 1;
  color: var(--purple);
  min-width: 2.2rem;
}}
.legend-name {{ font-weight: 700; font-size: .9rem; }}
.legend-row dd {{ margin: 0; font-size: .9rem; }}

.cmd-block {{ margin-top: .5rem; }}
.cmd-head {{
  margin: 0 0 .6rem;
  font-family: var(--display);
  font-size: 1.25rem;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--purple);
}}
.cmd-table {{ width: 100%; border-collapse: collapse; }}
.cmd-table tr {{ border-bottom: 1px solid rgba(20,20,16,.14); }}
.cmd-table tr:last-child {{ border-bottom: 0; }}
.cmd-table th {{
  text-align: left;
  padding: .4rem .75rem .4rem 0;
  width: 9.5rem;
  vertical-align: baseline;
}}
.cmd-table td {{ padding: .4rem 0; font-size: .93rem; vertical-align: baseline; }}

.kbd {{
  display: inline-block;
  font-family: var(--body);
  font-weight: 700;
  font-size: .85rem;
  letter-spacing: .04em;
  background: var(--ink);
  color: var(--chartreuse);
  border-radius: 7px;
  padding: .2rem .55rem;
  white-space: nowrap;
}}
.kbd-phrase {{ background: var(--purple); color: #fff; font-weight: 600; letter-spacing: .01em; }}

.callout {{
  border: 3px solid var(--purple);
  border-radius: 16px;
  padding: 1.1rem 1.3rem;
  background: rgba(107,24,212,.06);
}}
.callout h3 {{
  margin: 0 0 .45rem;
  font-family: var(--display);
  font-size: 1.15rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--purple);
}}
.callout p {{ margin: 0; font-size: .93rem; }}

/* ---------- Sections ---------- */
.section {{
  background: var(--paper);
  border: 4px solid var(--ink);
  padding: 0 0 2rem;
  overflow: hidden;
}}
.sec-head {{
  background: var(--chartreuse);
  border-bottom: 4px solid var(--ink);
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) 82px;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 1.25rem;
}}
.sec-deco {{ height: 150px; overflow: hidden; opacity: .9; }}
.sec-deco .squiggle {{ height: 150px; width: 82px; }}
.sec-headtext {{ text-align: center; }}
.sec-num {{
  margin: 0;
  font-family: var(--display);
  font-size: .95rem;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--purple);
}}
.sec-title {{
  margin: .25rem 0 .4rem;
  font-family: var(--display);
  font-size: clamp(2rem, 6.5vw, 3.4rem);
  line-height: .92;
  text-transform: uppercase;
  text-wrap: balance;
}}
.sec-count {{
  margin: 0;
  display: inline-block;
  background: var(--ink);
  color: var(--chartreuse);
  border-radius: 20px;
  padding: .18rem .8rem;
  font-size: .72rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  font-weight: 700;
}}
.sec-intro {{
  margin: 1.75rem 2.5rem 0;
  font-size: 1.02rem;
  font-weight: 500;
  max-width: 64ch;
}}

.notice {{
  margin: 1.5rem 2.5rem 0;
  border: 3px dashed var(--orange);
  border-radius: 16px;
  padding: 1.1rem 1.3rem;
  background: rgba(226,98,43,.08);
}}
.notice h3 {{
  margin: 0 0 .45rem;
  font-family: var(--display);
  font-size: 1.05rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--orange);
}}
.notice p {{ margin: 0; font-size: .9rem; }}

.group {{ margin: 2rem 2.5rem 0; }}
.group-head {{
  display: flex;
  align-items: baseline;
  gap: .9rem;
  flex-wrap: wrap;
  border-bottom: 3px solid var(--ink);
  padding-bottom: .5rem;
  margin-bottom: 1.1rem;
}}
.group-title {{
  margin: 0;
  font-family: var(--display);
  font-size: 1.4rem;
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.group-path {{
  margin: 0;
  font-size: .78rem;
  font-weight: 600;
  color: var(--purple);
  background: rgba(107,24,212,.1);
  border-radius: 20px;
  padding: .15rem .7rem;
}}
.group-note {{ margin: -.5rem 0 1rem; font-size: .88rem; color: var(--olive); font-weight: 500; }}

.tips {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(19rem, 1fr)); gap: .9rem; }}
.tip {{
  background: #fff;
  border: 2px solid rgba(20,20,16,.16);
  border-radius: 14px;
  padding: .95rem 1.05rem 1rem;
  display: flex;
  flex-direction: column;
  gap: .45rem;
  break-inside: avoid;
}}
.tip-gold {{ border-color: var(--orange); border-width: 3px; background: #FFFCF6; }}
.tip-todo {{ border-style: dashed; border-color: var(--purple); background: #FBF7FF; }}
.tip-head {{ display: flex; gap: .6rem; align-items: baseline; }}
.tip-num {{
  font-family: var(--display);
  font-size: .95rem;
  color: var(--purple);
  font-variant-numeric: tabular-nums;
  letter-spacing: .04em;
}}
.tip-gold .tip-num {{ color: var(--orange); }}
.tip-title {{ margin: 0; font-size: 1rem; line-height: 1.25; font-weight: 700; text-wrap: balance; }}
.tip-body {{ margin: 0; font-size: .88rem; line-height: 1.55; }}
.tip-keys {{ margin-top: auto; padding-top: .2rem; }}
.badge {{
  align-self: flex-start;
  font-size: .62rem;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
  border-radius: 20px;
  padding: .15rem .6rem;
}}
.badge-gold {{ background: var(--orange); color: #fff; }}
.badge-todo {{ background: var(--purple); color: #fff; }}

.totop {{ margin: 2rem 2.5rem 0; }}
.totop a {{
  font-family: var(--display);
  font-size: .82rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--purple);
  text-decoration: none;
  border-bottom: 2px solid var(--purple);
}}
.doc .totop {{ margin-left: 0; margin-right: 0; }}

/* ---------- Outro ---------- */
.outro {{
  background: var(--ink);
  color: var(--paper);
  border: 4px solid var(--ink);
  padding: 4.5rem 3rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.outro-inner {{ position: relative; z-index: 2; }}
.outro-title {{
  margin: 0 0 1.25rem;
  font-family: var(--display);
  font-size: clamp(2.4rem, 8vw, 4.2rem);
  line-height: .95;
  text-transform: uppercase;
  color: var(--chartreuse);
}}
.outro-lead {{ margin: 0 auto 1rem; max-width: 44ch; font-size: 1.05rem; }}
.outro-note {{ margin: 0 auto; max-width: 46ch; font-size: .92rem; color: #C9CAB4; }}
.outro-mark {{
  margin: 2.5rem 0 0;
  font-family: var(--display);
  font-size: 1rem;
  letter-spacing: .24em;
  text-transform: uppercase;
  color: var(--orange);
}}

/* ---------- Responsive ---------- */
@media (max-width: 1000px) {{
  .shell {{ grid-template-columns: 1fr; }}
  .rail {{
    position: static;
    height: auto;
    max-height: 42vh;
  }}
  .rail-scroll {{ max-height: 32vh; }}
  .cover-squig, .toc-deco {{ display: none; }}
  .sec-head {{ grid-template-columns: 1fr; }}
  .sec-deco {{ display: none; }}
  .doc, .toc, .cover {{ padding-left: 1.35rem; padding-right: 1.35rem; }}
  .group, .sec-intro, .notice, .totop {{ margin-left: 1.35rem; margin-right: 1.35rem; }}
  .legend-row {{ grid-template-columns: 1fr; gap: .2rem; }}
}}

@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; transition: none !important; scroll-behavior: auto !important; }}
}}

html {{ scroll-behavior: smooth; }}

/* ---------- Print / PDF ---------- */
@page {{ size: A4; margin: 12mm 11mm; }}
/* Poster pages get their own page box with no margin so the colour bleeds to trim. */
@page bleed {{ size: A4; margin: 0; }}

@media print {{
  html {{ scroll-behavior: auto; }}
  /* Chromium drops background fills when printing unless a page opts in. */
  *, *::before, *::after {{
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{ background: #fff; font-size: 10.5pt; }}
  .rail, .totop {{ display: none !important; }}
  .shell {{ display: block; }}
  .book {{ display: block; padding: 0; gap: 0; }}
  .page {{
    max-width: none;
    border: none;
    break-after: page;
    page-break-after: always;
  }}
  .page:last-child {{ break-after: auto; page-break-after: auto; }}
  /* Poster pages bleed past the page margin to the paper edge. */
  .cover, .toc, .outro {{
    page: bleed;
    margin: 0;
    padding: 16mm 14mm;
    min-height: 297mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}
  /* Every contents entry has to land on one page, so tune the vertical rhythm. */
  .toc-kicker {{ font-size: 15pt; }}
  .toc-kicker .burst {{ width: 40px; height: 40px; }}
  .toc-title {{ font-size: 46pt; margin-bottom: 7mm; }}
  .toc-frame {{ padding: 6mm 7mm; }}
  .toc-row a {{ padding: .28rem .3rem; }}
  .toc-label {{ font-size: 10.5pt; }}
  .toc-go {{ font-size: 8pt; }}
  .toc-foot {{ margin-top: 6mm; }}
  .section, .doc {{ padding-left: 0; padding-right: 0; }}
  .group, .sec-intro, .notice {{ margin-left: 0; margin-right: 0; }}
  .sec-head {{ margin: 0 0 0; }}
  .group-head, .sec-head, .doc-head {{ break-after: avoid; page-break-after: avoid; }}
  .tips {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .tip, .callout, .notice, .legend-row, .cmd-block {{
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .toc-row a:hover {{ background: none; color: inherit; }}
}}
"""


# --------------------------------------------------------------------------
# Behaviour — scrollspy for the rail
# --------------------------------------------------------------------------
SCRIPT = """
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.rail-link'));
  var map = {};
  links.forEach(function (link) {
    var id = link.getAttribute('href').slice(1);
    map[id] = link;
  });
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  if (!('IntersectionObserver' in window)) return;
  var seen = new Set();
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { seen.add(entry.target.id); }
      else { seen.delete(entry.target.id); }
    });
    links.forEach(function (l) { l.classList.remove('is-active'); });
    for (var i = 0; i < pages.length; i++) {
      if (seen.has(pages[i].id) && map[pages[i].id]) {
        map[pages[i].id].classList.add('is-active');
        break;
      }
    }
  }, { rootMargin: '-15% 0px -70% 0px' });
  pages.forEach(function (p) { if (p.id) observer.observe(p); });
})();
"""


# --------------------------------------------------------------------------
def main():
    front, sections = load()
    total = count_tips(sections)

    body = [build_rail(front, sections), '<main class="book">']
    body.append(build_cover(front, total, len(sections)))
    body.append(build_toc(front, sections))
    for page in front["pages"]:
        body.append(build_front_page(page))

    counter = 1
    for section in sections:
        chunk, counter = build_section(section, counter)
        body.append(chunk)
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
    for s in sections:
        n = sum(len(g['tips']) for g in s['groups'])
        print(f"  {s['number']:>2}. {s['title']:<38} {n:>3} tricks")


if __name__ == "__main__":
    main()
