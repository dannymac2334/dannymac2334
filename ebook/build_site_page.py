#!/usr/bin/env python3
"""Build the searchable web library for the Logic Pro Crash Course.

A single self-contained page in the dannny mcccarthy rates design (brand.py):
Figtree and the signature are embedded, nothing is loaded from the site, so the
page looks the same opened from a download, a preview or the live site.

The page exists to answer one question — "how do I do the thing I want to do?"
— so search is the centre of it. Typing switches the page from the book view
into one ranked list of results, best match first, with the section each trick
comes from. See SEARCH_JS for how a beginner's words are matched.

Output: dist/logic-pro-crash-course-page.html
"""

import json
import pathlib

import brand
from build import (esc, keycap, load, slug, count_tips, sources_html, numbered_refs, legal_notice,
                   load_extras, term_pattern, link_terms)

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# Delivered as a file alongside the PDF (Gumroad), so it links to nothing on a server:
# it has to work opened straight from someone's Downloads folder.
HIGHLIGHT = "GAME CHANGER"

TITLE = "Logic Pro Crash Course | dannny mcccarthy"
_front, _sections = load()
TRICKS = count_tips(_sections)
DESC = (f"{TRICKS} Logic Pro tricks across {len(_sections)} sections, searchable by what you want to do. "
        "Every trick cites its source.")
URL = "https://www.dannnymcccarthy.com/logic-pro-crash-course"

# Everyday words a beginner types, mapped to the words the book actually uses.
# Only true equivalents go here, and every target word appears in content/ —
# test_search.py fails the build if a target matches nothing.
SYNONYMS = {
    "autotune": ["pitch", "flex pitch", "tuning"],
    "auto-tune": ["pitch", "flex pitch", "tuning"],
    "tune": ["tuning", "pitch", "flex pitch"], "tuned": ["tuning", "pitch", "flex pitch"],
    "voice": ["vocal"], "sing": ["vocal"], "singer": ["vocal"], "singing": ["vocal"], "vocalist": ["vocal"],
    "export": ["bounce", "share"], "mp3": ["bounce"], "render": ["bounce"], "wav": ["bounce", "wav"],
    "bpm": ["tempo"], "speed": ["tempo", "speed"],
    "quiet": ["volume", "gain"], "quieter": ["volume", "gain"], "softer": ["volume", "gain"],
    "loud": ["louder", "volume", "gain", "compressor"],
    "echo": ["delay", "tape delay"],
    "reverb": ["reverb", "chromaverb", "space designer"], "verb": ["reverb", "chromaverb", "space designer"],
    "equalizer": ["eq"], "equaliser": ["eq"],
    "panning": ["pan"],
    "headphones": ["headphone"],
    "microphone": ["mic", "record"],
    "melody": ["melod", "note"], "melodies": ["melod", "note"],
    "chop": ["slice", "split", "sampler"],
    "hihat": ["hi-hat"], "hihats": ["hi-hat"], "hat": ["hi-hat"], "hats": ["hi-hat"],
    "arp": ["arpeggiator"],
    "beat": ["drum", "beat"], "beats": ["drum", "beat"],
    "sidechain": ["side-chain", "side chain", "sidechain"],
    "shortcut": ["key command"], "shortcuts": ["key command"], "hotkey": ["key command"], "hotkeys": ["key command"],
    "timing": ["quantize", "quantise", "timing", "flex time"],
    "quantize": ["quantise", "quantize"], "quantise": ["quantize", "quantise"],
    "color": ["colour", "color"], "colors": ["colour", "color"], "colour": ["colour", "color"],
    "remove": ["delete", "remove"], "erase": ["delete"],
    "metronome": ["metronome", "click sound"],
    "cut": ["cut", "split", "scissors", "trim"],
    "typing": ["musical typing"],
    "countin": ["count-in", "count in"],
    "master": ["master", "mastering"],
    "split": ["split", "stem splitter", "slice"],
    "stems": ["stem"],
    "keyboard": ["keyboard", "musical typing"],
    "piano": ["piano"],
}

STOP = ("a an the to i im i'm want wanna how do does can could my me in on of for with and or is it "
        "what make making made get some this that you your use using logic pro way ways into from "
        "at by be should would will please help just")


# --------------------------------------------------------------------------
# Content renderers
# --------------------------------------------------------------------------
EXTRA = {"rx": None, "lookup": {}, "defs": {}, "goals": {}}


def gl_span(txt, gid):
    """Jargon inside a trick: tap or hover for the plain-English meaning."""
    d = EXTRA["defs"].get(gid, "")
    return (f'<span class="lp-gl" tabindex="0" data-def="{esc(d).replace(chr(34), "&quot;")}">'
            f'{txt}</span>')


def kcaps(keys):
    k = keycap(keys).replace('class="kbd kbd-phrase"', 'class="lp-kbd phrase"')
    return k.replace('class="kbd"', 'class="lp-kbd"')


def tip(t, i, where):
    keys = t.get("k")
    cls = "lp-tip" + (" is-key" if t.get("b") == HIGHLIGHT else "")
    goals = t.get("goals", [])
    words = " ".join(w for g in goals for w in [EXTRA["goals"].get(g, {}).get("label", ""),
                                                  *EXTRA["goals"].get(g, {}).get("synonyms", [])])
    out = [f'<article class="{cls}" id="t-{i}" data-n="{i}" data-goals="{" ".join(goals)}" '
           f'data-lvl="{t.get("lvl", 2)}" data-k="{esc(words)}" data-keys="{esc(keys or "")}" '
           f'data-where="{esc(where)}">', '<div class="lp-tip-head">',
           f'<span class="lp-num">No. {i:03d}</span>']
    if t.get("lvl") == 1:
        out.append('<span class="lp-badge lp-start">Start here</span>')
    if t.get("b"):
        out.append(f'<span class="lp-badge">{esc(t["b"])}</span>')
    out.append("</div>")
    out.append(f'<p class="lp-where">{esc(where)}</p>')
    out.append(f'<h4>{esc(t["t"])}</h4>')
    out.append(f'<p class="lp-body">{link_terms(esc(t["d"]), EXTRA["rx"], EXTRA["lookup"], gl_span)}</p>')
    if keys:
        out.append(f'<div class="lp-keys">{kcaps(keys)}</div>')
    if t.get("src"):
        out.append(sources_html(t["src"], cls="lp-src"))
    out.append("</article>")
    return "".join(out)


def extra_items(front):
    """Start Here steps and key-table rows, as hidden search-only cards.

    A beginner's first questions ("how do I play without a keyboard?", "what
    does ⌘K do?") are answered in the front matter, not in the tricks, so
    search has to reach it too. Each item links back to where it lives.
    """
    out = []
    for p in front["pages"]:
        for n, st in enumerate(p.get("steps", []), 1):
            out.append(dict(t=st["title"], d=st["body"], k=st.get("key"), src=st.get("src"),
                            where=f'{p["label"]} · Step {n}', href=f'#{p["id"]}', label=f"Step {n}"))
        for tb in p.get("tables", []):
            for row in tb["rows"]:
                out.append(dict(t=row[1], d=f'Key command: {row[0]}.', k=row[0],
                                src=row[2] if len(row) > 2 else None,
                                where=f'{p["label"]} · {tb["heading"]}', href=f'#{p["id"]}', label="Key command"))
    html = []
    for it in out:
        html.append(f'<article class="lp-tip" data-n="0" data-lvl="1" data-goals="start" data-k="" '
                    f'data-keys="{esc(it["k"] or "")}" data-where="{esc(it["where"])}" data-href="{it["href"]}">'
                    f'<div class="lp-tip-head"><span class="lp-num">{esc(it["label"])}</span>'
                    '<span class="lp-badge lp-start">Start here</span></div>'
                    f'<p class="lp-where">{esc(it["where"])}</p><h4>{esc(it["t"])}</h4>'
                    f'<p class="lp-body">{esc(it["d"])}</p>'
                    + (f'<div class="lp-keys">{kcaps(it["k"])}</div>' if it["k"] else "")
                    + (sources_html(it["src"], cls="lp-src") if it["src"] else "") + "</article>")
    return '<div class="lp-extra" hidden>' + "".join(html) + "</div>"


def block_open(bid, tone, kicker, title, extra_cls=""):
    return [f'<section class="lp-block {tone}{extra_cls}" id="{bid}"><div class="lp-wrap">',
            f'<p class="kicker">{kicker}</p>', f'<h2 class="sec-title">{title}</h2>']


def front_block(p, tone):
    o = block_open(p["id"], tone, esc(p["kicker"]), esc(p["title"]), " lp-doc")
    for para in p.get("body", []):
        o.append(f'<p class="sec-lede">{esc(para)}</p>')
    if p.get("steps"):
        o.append('<ol class="lp-steps">')
        for n, st in enumerate(p["steps"], 1):
            k = f'<div class="lp-keys">{kcaps(st["key"])}</div>' if st.get("key") else ""
            o.append(f'<li><span class="lp-step-n">{n}</span><div><h3>{esc(st["title"])}</h3>'
                     f'<p>{link_terms(esc(st["body"]), EXTRA["rx"], EXTRA["lookup"], gl_span)}</p>{k}'
                     + (sources_html(st["src"], cls="lp-src") if st.get("src") else "")
                     + "</div></li>")
        o.append("</ol>")
    if p.get("generated") == "goals":
        o.append('<div class="lp-goal-grid">' + "".join(
            f'<button class="lp-goal-btn" type="button" data-goal="{g["id"]}">'
            f'<span class="label">{EXTRA["goal_counts"].get(g["id"], 0)} tricks</span>'
            f'<b>{esc(g["label"])}</b></button>'
            for g in EXTRA["goal_list"] if EXTRA["goal_counts"].get(g["id"])) + "</div>")
    if p.get("generated") == "glossary":
        o.append('<dl class="lp-gloss">' + "".join(
            f'<div id="g-{e["id"]}"><dt>{esc(e["term"])}'
            + (f'<small>also: {esc(", ".join(e["aka"]))}</small>' if e.get("aka") else "")
            + f'</dt><dd>{esc(e["def"])}'
            + (sources_html(e["src"], cls="lp-src") if e.get("src") else "") + "</dd></div>"
            for e in sorted(EXTRA["glossary"], key=lambda e: e["term"].lower())) + "</dl>")
    if p.get("list"):
        o.append('<ul class="lp-rules">' + "".join(f"<li>{esc(x)}</li>" for x in p["list"]) + "</ul>")
    if p.get("keys"):
        marks, refs = numbered_refs([k.get("src") for k in p["keys"]])
        o.append('<dl class="lp-legend">')
        for k, mark in zip(p["keys"], marks):
            o.append(f'<div><dt><span class="lp-sym">{esc(k["sym"])}</span>'
                     f'<b>{esc(k["name"])}</b></dt><dd>{esc(k["note"])}{mark}</dd></div>')
        o.append("</dl>")
        o.append(refs.replace('class="doc-src"', 'class="lp-src"'))
    for tb in p.get("tables", []):
        o.append(f'<div class="lp-table-wrap"><h3 class="lp-sub">{esc(tb["heading"])}</h3>'
                 '<table class="lp-table"><tbody>')
        marks, refs = numbered_refs([row[2] if len(row) > 2 else None for row in tb["rows"]])
        for (key, d, *_), mark in zip(tb["rows"], marks):
            o.append(f'<tr><th><span class="lp-kbd">{esc(key)}</span></th><td>{esc(d)}{mark}</td></tr>')
        o.append("</tbody></table>" + refs.replace('class="doc-src"', 'class="lp-src"') + "</div>")
    if p.get("callout"):
        c = p["callout"]
        o.append(f'<aside class="lp-card lp-callout"><h3>{esc(c["title"])}</h3><p>{esc(c["text"])}</p>'
                 + (sources_html(c["src"], cls="lp-src") if c.get("src") else "") + '</aside>')
    o.append("</div></section>")
    return "".join(o)


def section_block(s, start, tone):
    total = sum(len(g["tips"]) for g in s["groups"])
    where = f'Section {s["number"]:02d} · {s["title"]}'
    o = block_open(slug(s), tone, f'Section {s["number"]:02d} &middot; {total} tricks', f'{esc(s["title"])}.')
    o.append(f'<p class="sec-lede">{esc(s["intro"])}</p>')
    if s.get("intro_src"):
        o.append(sources_html(s["intro_src"], cls="lp-src"))
    if s.get("notice"):
        n = s["notice"]
        o.append(f'<aside class="lp-card lp-notice"><h3>{esc(n["title"])}</h3><p>{esc(n["text"])}</p>'
                 + (sources_html(n["src"], cls="lp-src") if n.get("src") else "") + '</aside>')
    i = start
    for g in s["groups"]:
        o.append('<div class="lp-group"><div class="lp-group-head"><h3>' + esc(g["heading"]) + "</h3>")
        if g.get("path"):
            o.append(f'<p class="lp-path">{esc(g["path"])}</p>')
        o.append("</div>")
        if g.get("note"):
            o.append(f'<p class="lp-note">{esc(g["note"])}</p>')
        o.append('<div class="lp-tips">')
        for t in g["tips"]:
            o.append(tip(t, i, where))
            i += 1
        o.append("</div></div>")
    o.append("</div></section>")
    return "".join(o), i


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------
def page_css():
    return brand.font_faces() + brand.root_vars() + """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{font-family:var(--font);font-weight:400;line-height:1.5;background:var(--black);color:var(--white);overflow-x:clip}
a{color:inherit;text-decoration:none}
button,input{font:inherit;color:inherit}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* the rates system */
.lp-wrap{max-width:var(--maxw);margin:0 auto;width:100%}
.dark{background:var(--black);color:var(--white);--dim:var(--muted-dark);--line:var(--line-dark);--soft:var(--label)}
.paper{background:var(--paper);color:var(--ink);--dim:var(--muted-light);--line:var(--line-light);--soft:var(--muted-light)}
.kicker{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.24em;color:var(--kicker);margin-bottom:clamp(20px,4vh,38px)}
.paper .kicker{color:var(--muted-light)}
.sec-title{font-weight:700;font-size:clamp(34px,6.4vw,104px);line-height:.96;letter-spacing:-.048em;max-width:18ch}
.sec-lede{margin-top:clamp(20px,3vh,32px);max-width:60ch;font-size:clamp(15px,1.3vw,19px);color:var(--dim)}
.pill{display:inline-flex;align-items:center;justify-content:center;padding:20px 46px;border:2px solid currentColor;
  border-radius:100px;font-weight:500;text-transform:uppercase;letter-spacing:.24em;font-size:12px;cursor:pointer;background:none;
  transition:background .35s var(--ease),color .35s var(--ease),transform .35s var(--ease)}
.dark .pill:hover{background:#fff;color:#000}
.paper .pill:hover{background:#000;color:#fff}
.pill:active{transform:scale(.97)}
.sig{display:block;width:clamp(150px,16vw,230px);height:auto;margin-bottom:clamp(22px,4vh,40px);filter:invert(1)}

/* hero */
.lp-hero{padding:clamp(72px,14vh,170px) var(--pad) clamp(56px,9vh,110px)}
.lp-hero h1{font-weight:700;font-size:clamp(40px,8.4vw,140px);line-height:.94;letter-spacing:-.048em;max-width:14ch}
.lp-hero .lede{margin-top:clamp(30px,5vh,54px);max-width:56ch;font-size:clamp(16px,1.6vw,22px);color:var(--muted-dark)}
.lp-hero .lede a{text-decoration:underline;text-underline-offset:3px}
.lp-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(12px,2vw,26px);margin-top:clamp(40px,7vh,80px)}
.lp-stat{border:1px solid var(--line-dark);border-radius:16px;padding:clamp(20px,2.6vw,34px)}
.label{display:block;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.2em;color:var(--label)}
.paper .label{color:var(--muted-light)}
.lp-stat b{display:block;margin:12px 0 4px;font-weight:700;font-size:clamp(38px,4.4vw,64px);line-height:1;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.lp-stat span:last-child{font-size:13px;color:var(--label)}
.lp-ctas{display:flex;gap:14px;flex-wrap:wrap;margin-top:clamp(30px,5vh,54px)}
.pill.solid{background:#fff;color:#000;border-color:#fff}
.dark .pill.solid:hover{background:transparent;color:#fff}

/* search bar — the centre of the page */
.lp-tools{position:sticky;top:0;z-index:50;background:rgba(0,0,0,.94);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border-top:1px solid var(--line-dark);border-bottom:1px solid var(--line-dark);padding:14px var(--pad)}
.lp-tools .lp-wrap{display:flex;flex-wrap:wrap;gap:10px 12px;align-items:center}
.lp-search{position:relative;flex:1 1 360px;min-width:0}
.lp-search svg{position:absolute;left:20px;top:50%;transform:translateY(-50%);width:18px;height:18px;pointer-events:none}
.lp-search input{width:100%;background:#0d0d0d;border:1px solid #3a3a3a;border-radius:100px;color:#fff;font-size:17px;
  padding:16px 96px 16px 50px;outline:none;transition:border-color .25s var(--ease)}
.lp-search input::placeholder{color:#fff;opacity:1}
.lp-search input:focus{border-color:#fff}
.lp-search input::-webkit-search-cancel-button{display:none}
.lp-clear{position:absolute;right:10px;top:50%;transform:translateY(-50%);border:0;background:#fff;color:#000;border-radius:100px;
  font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:8px 14px;cursor:pointer;display:none}
.lp-search.has-q .lp-clear{display:block}
.lp-slash{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-size:11px;color:#fff;border:1px solid #fff;border-radius:6px;padding:2px 8px;pointer-events:none}
.lp-search.has-q .lp-slash{display:none}
.lp-toggle{flex:0 0 auto;cursor:pointer;background:transparent;color:#fff;border:1px solid #3a3a3a;border-radius:100px;
  font-weight:500;font-size:11px;text-transform:uppercase;letter-spacing:.16em;padding:14px 20px;white-space:nowrap;
  transition:background .25s var(--ease),border-color .25s var(--ease),color .25s var(--ease)}
.lp-toggle:hover{border-color:#fff}
.lp-toggle[aria-pressed="true"]{background:#fff;border-color:#fff;color:#000}
.lp-goal-on{display:none;flex:0 0 auto;cursor:pointer;border:0;border-radius:100px;background:#fff;color:#000;font-size:13px;font-weight:600;padding:12px 18px}
.lp-goal-on.show{display:inline-flex;gap:8px;align-items:center}
.lp-nav{flex:1 0 100%;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding-top:2px}
.lp-nav::-webkit-scrollbar{display:none}
.lp-nav a{flex:0 0 auto;font-size:12px;color:#fff;border:1px solid #3a3a3a;border-radius:100px;padding:7px 14px;white-space:nowrap;
  transition:color .25s var(--ease),border-color .25s var(--ease)}
.lp-nav a:hover{border-color:#fff}
.lp-nav a.active{background:#fff;color:#000;border-color:#fff}
.lp-nav a i{font-style:normal;font-weight:700;margin-right:6px;font-variant-numeric:tabular-nums}
.is-filtering .lp-nav{display:none}

/* blocks */
.lp-block{padding:clamp(64px,12vh,150px) var(--pad);scroll-margin-top:120px}
.is-filtering .lp-book{display:none}
.lp-results{display:none;padding-top:clamp(36px,6vh,72px)}
.is-filtering .lp-results{display:block}
.lp-results .sec-title{font-size:clamp(30px,5vw,72px);max-width:22ch}
.lp-hint{margin-top:18px;font-size:15px;color:var(--dim)}
.lp-hint button{border:0;background:none;text-decoration:underline;text-underline-offset:3px;cursor:pointer;font-size:inherit;color:inherit}

.lp-group{margin-top:clamp(44px,7vh,90px)}
.lp-group-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding-bottom:12px;border-bottom:1px solid var(--line)}
.lp-group-head h3{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em}
.lp-path{font-size:13px;color:var(--soft)}
.lp-note{margin-top:14px;font-size:14px;color:var(--soft)}
.lp-tips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(16px,2vw,26px);margin-top:clamp(24px,4vh,40px)}

/* trick card = the rates tier card */
.lp-tip{border:1px solid var(--line);border-radius:16px;padding:clamp(24px,2.6vw,36px);display:flex;flex-direction:column;
  transition:border-color .35s var(--ease),transform .35s var(--ease)}
.lp-tip:hover{transform:translateY(-2px);border-color:var(--soft)}
.lp-tip-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.lp-num{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.2em;color:var(--soft);font-variant-numeric:tabular-nums}
.lp-badge{font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;border-radius:100px;padding:4px 11px;background:currentColor}
.lp-badge{background:var(--ink);color:var(--white)}
.dark .lp-badge{background:var(--white);color:var(--black)}
.lp-badge.lp-start{background:transparent;color:inherit;border:1px solid currentColor}
.lp-where{display:none;margin-top:10px;font-size:12px;color:var(--soft)}
.lp-results .lp-where{display:block}
.lp-tip h4{margin-top:10px;font-weight:700;font-size:clamp(18px,1.6vw,22px);line-height:1.2;letter-spacing:-.02em}
.lp-body{margin-top:12px;font-size:15px;line-height:1.6;color:var(--dim);flex:1}
.lp-keys{margin-top:16px;display:flex;gap:6px;flex-wrap:wrap}
.lp-src{margin-top:18px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;line-height:1.5;color:var(--soft)}
.lp-src span{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;margin-right:6px}
.lp-src a{text-decoration:underline;text-underline-offset:2px;text-decoration-color:currentColor}
.lp-src a:hover{text-decoration-color:currentColor}
/* game changer: the opposite tier colour */
.paper .lp-tip.is-key{background:var(--black);color:var(--white);border-color:var(--black);--dim:var(--muted-dark);--line:var(--line-dark);--soft:var(--label)}
.paper .lp-tip.is-key .lp-badge{background:var(--white);color:var(--black)}
.paper .lp-tip.is-key .lp-badge.lp-start{background:transparent;color:inherit}
.dark .lp-tip.is-key{background:var(--paper);color:var(--ink);border-color:var(--paper);--dim:var(--muted-light);--line:var(--line-light);--soft:var(--muted-light)}
.dark .lp-tip.is-key .lp-badge{background:var(--ink);color:var(--white)}
.dark .lp-tip.is-key .lp-badge.lp-start{background:transparent;color:inherit}
.lp-kbd{display:inline-block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;border-radius:100px;
  padding:.4rem .85rem;white-space:nowrap;background:var(--ink);color:var(--white)}
.dark .lp-kbd,.paper .is-key .lp-kbd{background:var(--white);color:var(--black)}
.dark .is-key .lp-kbd{background:var(--ink);color:var(--white)}
.lp-kbd.phrase{background:transparent !important;color:inherit !important;border:1px solid var(--line)}
.lp-tip mark{background:color-mix(in srgb,currentColor 14%,transparent);color:inherit;border-radius:3px;padding:0 1px}

.lp-gl{position:relative;cursor:help;text-decoration:underline dotted;text-underline-offset:3px;outline:none}
.lp-gl:hover::after,.lp-gl:focus::after{content:attr(data-def);position:absolute;left:0;bottom:calc(100% + 8px);z-index:30;
  width:min(280px,70vw);background:var(--ink);color:#fff;font-size:13px;line-height:1.5;font-weight:400;letter-spacing:0;
  text-transform:none;padding:12px 14px;border-radius:12px;box-shadow:0 12px 30px -12px rgba(0,0,0,.5);white-space:normal}
.dark .lp-gl:hover::after,.dark .lp-gl:focus::after{background:#fff;color:#000}

/* definition cards above search results */
.lp-defs{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:clamp(16px,2vw,26px);margin-top:clamp(24px,4vh,40px)}
.lp-defs:empty{display:none}
.lp-def{border:1px solid var(--line);border-radius:16px;padding:clamp(20px,2.4vw,30px);background:var(--black);color:var(--white)}
.lp-def b{display:block;margin-top:10px;font-size:22px;letter-spacing:-.02em}
.lp-def p{margin-top:8px;font-size:15px;color:var(--muted-dark)}

/* front matter */
.lp-card{border:1px solid var(--line);border-radius:16px;padding:clamp(24px,3.4vw,44px);margin-top:clamp(30px,5vh,54px);max-width:900px}
.lp-card h3{font-weight:700;font-size:clamp(18px,1.8vw,24px);letter-spacing:-.02em;line-height:1.2}
.lp-card p{margin-top:12px;font-size:15px;color:var(--dim)}
.lp-steps{list-style:none;margin-top:clamp(30px,5vh,54px);max-width:900px}
.lp-steps li{display:grid;grid-template-columns:64px 1fr;gap:16px;border-top:1px solid var(--line);padding:24px 0}
.lp-step-n{font-size:40px;font-weight:700;letter-spacing:-.048em;line-height:1}
.lp-steps h3{font-size:clamp(18px,1.8vw,24px);letter-spacing:-.02em;line-height:1.2}
.lp-steps p{margin-top:8px;color:var(--dim);font-size:15px;max-width:64ch}
.lp-goal-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(12px,1.6vw,20px);margin-top:clamp(30px,5vh,54px)}
.lp-goal-btn{cursor:pointer;text-align:left;background:transparent;border:1px solid var(--line);border-radius:16px;padding:22px 24px;
  transition:border-color .3s var(--ease),background .3s var(--ease),color .3s var(--ease)}
.lp-goal-btn b{display:block;margin-top:8px;font-size:clamp(17px,1.5vw,21px);letter-spacing:-.02em;line-height:1.2}
.paper .lp-goal-btn:hover{background:var(--black);color:var(--white);border-color:var(--black)}
.dark .lp-goal-btn:hover{background:var(--white);color:var(--black);border-color:var(--white)}
.lp-goal-btn:hover .label{color:inherit}
.lp-rules{list-style:none;margin-top:clamp(30px,5vh,54px);max-width:900px;border-top:1px solid var(--line)}
.lp-rules li{position:relative;padding:14px 0 14px 22px;border-bottom:1px solid var(--line);color:var(--dim);font-size:15px}
.lp-rules li::before{content:"";position:absolute;left:0;top:1.45em;width:8px;height:1px;background:currentColor;opacity:.5}
.lp-legend{margin-top:clamp(30px,5vh,54px);max-width:900px;border-top:1px solid var(--line)}
.lp-legend div{display:grid;grid-template-columns:14rem minmax(0,1fr);gap:1.2rem;align-items:baseline;padding:14px 0;border-bottom:1px solid var(--line)}
.lp-legend dt{display:flex;align-items:baseline;gap:1rem}
.lp-sym{font-size:26px;font-weight:500;line-height:1;min-width:2rem}
.lp-legend dt b{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em}
.lp-legend dd{font-size:15px;color:var(--dim)}
.lp-table-wrap{margin-top:clamp(30px,5vh,54px);max-width:900px}
.lp-sub{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;padding-bottom:12px;border-bottom:1px solid var(--line)}
.lp-table{width:100%;border-collapse:collapse}
.lp-table tr{border-bottom:1px solid var(--line)}
.lp-table th{text-align:left;padding:10px 20px 10px 0;width:11rem;vertical-align:baseline}
.lp-table td{padding:10px 0;font-size:15px;color:var(--dim);vertical-align:baseline}
.lp-gloss{margin-top:clamp(30px,5vh,54px);columns:2 320px;column-gap:44px}
.lp-gloss>div{break-inside:avoid;border-top:1px solid var(--line);padding:14px 0;scroll-margin-top:140px}
.lp-gloss dt{font-weight:700;font-size:18px;letter-spacing:-.02em}
.lp-gloss dt small{display:block;font-weight:400;font-size:12px;color:var(--soft);margin-top:2px;letter-spacing:0}
.lp-gloss dd{margin-top:6px;color:var(--dim);font-size:14.5px}
.lp-gloss .lp-src{margin-top:8px;padding-top:0;border:0}
sup.ref{font-size:10px;font-weight:600;margin-left:3px;color:var(--soft)}
.ref-n{font-weight:600;font-size:10px}
.lp-table-wrap .lp-src,.lp-legend+.lp-src{border:0;padding-top:0}

.lp-end{padding:clamp(64px,12vh,150px) var(--pad)}
.foot{padding:clamp(40px,7vh,80px) var(--pad);border-top:1px solid var(--line-dark);display:flex;justify-content:space-between;
  align-items:flex-end;gap:24px;flex-wrap:wrap;font-size:13px;color:var(--kicker)}
.foot .mark-sig{display:block;width:150px;height:auto;filter:invert(1)}
.lp-legal{padding:0 var(--pad) 40px;font-size:11px;line-height:1.6;color:var(--kicker)}
.lp-legal p{max-width:var(--maxw);margin:0 auto}
.lp-top{position:fixed;right:20px;bottom:20px;z-index:60;opacity:0;pointer-events:none;transform:translateY(8px);
  transition:opacity .3s var(--ease),transform .3s var(--ease);background:#fff;color:#000;border:0;border-radius:100px;cursor:pointer;
  font-weight:600;font-size:11px;letter-spacing:.16em;text-transform:uppercase;padding:14px 20px;box-shadow:0 8px 24px -8px rgba(0,0,0,.4)}
.lp-top.show{opacity:1;pointer-events:auto;transform:none}

@media(max-width:1100px){.lp-tips,.lp-goal-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){
  .lp-tips,.lp-goal-grid{grid-template-columns:1fr}
  .lp-stats{gap:8px;margin-top:32px}
  .lp-stat{padding:14px 12px;border-radius:12px}
  .lp-stat b{font-size:30px;margin:8px 0 0}
  .lp-stat span:last-child{display:none}
  .lp-stat .label{font-size:10px;letter-spacing:.14em}
  .lp-hero{padding-top:48px;padding-bottom:40px}
  .sig{width:130px}
  .lp-ctas .pill{padding:16px 28px}
  .lp-legend div{grid-template-columns:1fr;gap:.3rem}
  .lp-table th{width:7rem}
  .lp-search input{font-size:16px}
  .lp-tools{padding:10px 16px}
  .lp-search{flex-basis:100%}
  .lp-search input{padding:13px 84px 13px 44px}
  .lp-search svg{left:16px}
  .lp-toggle{padding:8px 13px;font-size:10px;letter-spacing:.12em}
  .lp-results .sec-title{font-size:32px}
  .lp-block{scroll-margin-top:170px}
}
@media(prefers-reduced-motion:reduce){*{transition:none !important}html{scroll-behavior:auto}}
"""


SEARCH_JS = r"""
<script>
(function () {
  /* ---------- search: find the trick for what you want to do ----------
     1. The query is split into words; filler ("how do I", "make", "my") is dropped.
     2. Each word is widened: plurals and -ing forms, and everyday words mapped to
        the book's words (autotune -> pitch, export -> bounce, bpm -> tempo).
     3. A word that matches nothing is corrected to the closest word in the book
        (quantise/quantize, reverbe -> reverb).
     4. Every trick is scored — title and goal matches count most — and the
        results are shown as one list, best first. If no trick has every word,
        the closest matches are shown and the page says so. */
  var CFG = JSON.parse(document.getElementById('lp-search-cfg').textContent);
  var STOP = ' ' + CFG.stop + ' ';
  var SYN = CFG.syn;
  var page = document.body;
  var input = document.getElementById('lp-q');
  var box = input.parentNode;
  var gcBtn = document.getElementById('lp-gc');
  var stBtn = document.getElementById('lp-start');
  var goalOn = document.getElementById('lp-goal-on');
  var out = document.getElementById('lp-out');
  var title = document.getElementById('lp-res-title');
  var hint = document.getElementById('lp-res-hint');
  var defsEl = document.getElementById('lp-defs');
  var gloss = CFG.gloss;
  var goalNames = CFG.goals;

  function norm(s) {
    return (' ' + s.toLowerCase().replace(/[‘’]/g, "'").replace(/[^a-z0-9#'⌘⌥⇧⌃+-]+/g, ' ')
      .replace(/\s+/g, ' ') + ' ');
  }
  var cards = Array.prototype.slice.call(document.querySelectorAll('.lp-book .lp-tip, .lp-extra .lp-tip'));
  var WEAK = ' fix fixing change changing add adding set setting turn create do go put better good best new thing things stuff '
           + 'quick quickly easy easily start starting open find show work working need song track tracks ';
  var vocab = {};
  var data = cards.map(function (c) {
    var h = c.querySelector('h4').textContent;
    var body = c.querySelector('.lp-body').textContent;
    var grp = c.closest('.lp-group');
    var group = grp ? grp.querySelector('h3').textContent : '';
    var d = {
      el: c, n: +c.getAttribute('data-n'), href: c.getAttribute('data-href'), lvl: c.getAttribute('data-lvl'),
      key: c.classList.contains('is-key'), goals: ' ' + c.getAttribute('data-goals') + ' ',
      t: norm(h), b: norm(body), k: norm(c.getAttribute('data-k') || ''),
      g: norm(group + ' ' + c.getAttribute('data-where')), keys: (c.getAttribute('data-keys') || '').toLowerCase()
    };
    (d.t + d.b + d.k + d.g).split(' ').forEach(function (w) { if (w.length > 2) vocab[w] = 1; });
    return d;
  });
  vocab = Object.keys(vocab);

  function words(q) {
    return norm(q).trim().split(' ').filter(function (w) { return w && STOP.indexOf(' ' + w + ' ') === -1; });
  }
  function variants(w) {
    var v = [w];
    var base = w.replace(/(ings|ing|ers|er|ed|es|s)$/, '');
    if (base.length >= 3 && base !== w) v.push(base);
    if (/y$/.test(w) && w.length > 4) v.push(w.slice(0, -1));
    (SYN[w] || SYN[base] || []).forEach(function (s) { v.push(s); });
    return v;
  }
  // a variant matches when some word in the field STARTS with it ("record" finds "recording")
  function has(field, v) { return field.indexOf(' ' + v) !== -1; }
  function anywhere(v) {
    for (var i = 0; i < data.length; i++) {
      var d = data[i];
      if (has(d.t, v) || has(d.b, v) || has(d.k, v) || has(d.g, v)) return true;
    }
    return false;
  }
  function dist(a, b) {
    if (Math.abs(a.length - b.length) > 2) return 9;
    var prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      cur = [i];
      for (j = 1; j <= b.length; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      }
      prev = cur;
    }
    return prev[b.length];
  }
  function correct(w) {
    if (w.length < 4) return null;
    var best = null, bd = w.length >= 8 ? 3 : 2;
    vocab.forEach(function (v) {
      var dd = dist(w, v);
      if (dd < bd) { bd = dd; best = v; }
    });
    return best;
  }

  // how well one card answers one query word: title beats body beats the card's goal tags
  function field(d, vs) {
    var best = 0;
    vs.forEach(function (v) {
      var s = 0;
      if (has(d.t, v)) s = v.indexOf(' ') !== -1 ? 14 : 10;   // "flex pitch" is more specific than "pitch"
      else if (has(d.b, v)) s = 5;
      else if (has(d.g, v)) s = 4;
      else if (has(d.k, v)) s = 3;
      if (d.keys && has(' ' + d.keys + ' ', v)) s = Math.max(s, 12);
      if (s > best) best = s;
    });
    return best;
  }
  // rare words decide the ranking; a word on half the cards ("region") barely moves it
  function score(d, groups, idf, weak, phrase) {
    var total = 0, matched = 0;
    groups.forEach(function (vs, i) {
      var f = field(d, vs);
      if (!f) return;
      if (!weak[i]) matched++;
      total += f * idf[i] * (weak[i] ? 0.3 : 1);
    });
    if (phrase) {
      if (has(d.t, phrase)) total += 25;
      else if (has(d.b, phrase)) total += 10;
    }
    return { s: total, m: matched };
  }

  var goal = '';
  function apply() {
    var raw = input.value.trim();
    box.classList.toggle('has-q', !!raw);
    var ws = words(raw);
    var fixed = [];
    var groups = ws.map(function (w) {
      var vs = variants(w);
      if (!vs.some(anywhere)) {
        var c = correct(w);
        if (c) { fixed.push([w, c]); vs = variants(c); }
      }
      return vs;
    });
    var gcOnly = gcBtn.getAttribute('aria-pressed') === 'true';
    var stOnly = stBtn.getAttribute('aria-pressed') === 'true';
    var filtering = !!raw || gcOnly || stOnly || !!goal;
    page.classList.toggle('is-filtering', filtering);
    goalOn.classList.toggle('show', !!goal);
    if (goal) goalOn.querySelector('span').textContent = goalNames[goal] || goal;
    if (!filtering) { out.innerHTML = ''; defsEl.innerHTML = ''; return; }

    var weak = ws.map(function (w) { return WEAK.indexOf(' ' + w + ' ') !== -1; });
    if (weak.every(Boolean)) weak = weak.map(function () { return false; });
    var idf = groups.map(function (vs) {
      var df = 0;
      // rarity is measured on what the tricks say, not on their broad goal tags
      data.forEach(function (d) { if (vs.some(function (v) { return has(d.t, v) || has(d.b, v); })) df++; });
      var w = Math.log(1 + data.length / Math.max(df, 1));
      return w * w;
    });
    var phrase = ws.length > 1 ? ws.join(' ') : '';
    var hits = [];
    data.forEach(function (d) {
      if (gcOnly && !d.key) return;
      if (stOnly && d.lvl !== '1') return;
      if (goal && d.goals.indexOf(' ' + goal + ' ') === -1) return;
      if (!groups.length && !d.n) return;
      var r = groups.length ? score(d, groups, idf, weak, phrase) : { s: 1, m: 0 };
      if (groups.length && !r.s) return;
      hits.push({ d: d, s: r.s, m: r.m });
    });
    var need = weak.filter(function (x) { return !x; }).length;
    // One ranked list. A trick missing one of the words is not dropped, it is
    // marked down: "tune my vocals" should still surface Flex Pitch, which
    // never says "vocals", but below tricks that say both.
    var floor = need > 1 ? Math.ceil(need / 2) : need;
    var full = hits.filter(function (h) { return h.m >= floor; });
    full.forEach(function (h) { h.r = need ? h.s * (0.35 + 0.65 * h.m / need) : h.s; });
    full.sort(function (a, b) { return b.r - a.r || (a.d.lvl - b.d.lvl) || a.d.n - b.d.n; });
    var partial = need > 1 && full.length && !full.some(function (h) { return h.m === need; });
    var shownAll = full.length;
    if (full.length > 36 && groups.length) full = full.slice(0, 36);
    out.innerHTML = '';
    var frag = document.createDocumentFragment();
    full.forEach(function (h) {
      var c = h.d.el.cloneNode(true);
      c.removeAttribute('id');
      var a = document.createElement('a');
      a.className = 'lp-num';
      a.href = h.d.href || '#t-' + h.d.n;
      a.textContent = (h.d.n ? 'No. ' + ('00' + h.d.n).slice(-3) : c.querySelector('.lp-num').textContent) + ' → in the book';
      a.addEventListener('click', function () { clearAll(); });
      c.querySelector('.lp-num').replaceWith(a);
      frag.appendChild(c);
    });
    out.appendChild(frag);

    var label = raw ? '“' + raw + '”' : (goal ? goalNames[goal] : (stOnly ? 'Start here' : 'Game changers'));
    title.textContent = full.length
      ? shownAll + (shownAll === 1 ? ' result for ' : ' results for ') + label + '.'
      : 'Nothing for ' + label + ' yet.';
    var notes = [];
    if (fixed.length) notes.push('Showing results for ' + fixed.map(function (f) { return '“' + f[1] + '”'; }).join(', ') + '.');
    if (shownAll > full.length) notes.push('Showing the best ' + full.length + '. Add a word to narrow it down.');
    if (partial) notes.push('No trick matches every word, so these are the closest.');
    if (!full.length) notes.push('Try one simple word — drums, vocals, loop, louder, tempo — or pick a goal below the search bar.');
    if (stOnly || gcOnly || goal) notes.push('Filters are on.');
    hint.innerHTML = '';
    notes.forEach(function (n) { hint.appendChild(document.createTextNode(n + ' ')); });
    if (stOnly || gcOnly || goal) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = 'Clear filters';
      b.addEventListener('click', function () { goal = ''; gcBtn.setAttribute('aria-pressed', 'false'); stBtn.setAttribute('aria-pressed', 'false'); apply(); });
      hint.appendChild(b);
    }
    showDefs(ws);
    // results always start at the top of the list, right under the search bar
    var tools = document.querySelector('.lp-tools');
    var y = document.querySelector('.lp-results').offsetTop - tools.offsetHeight;
    if (Math.abs(window.scrollY - y) > 2) window.scrollTo({ top: y, behavior: 'instant' });
    countEl.textContent = shownAll + ' results';
  }

  function showDefs(ws) {
    defsEl.innerHTML = '';
    if (!ws.length) return;
    var q = ws.join(' ');
    gloss.filter(function (e) {
      return [e.t].concat(e.a || []).some(function (n) {
        n = n.toLowerCase();
        return n === q || ws.indexOf(n) !== -1 || (n.length > 3 && q.indexOf(n) !== -1);
      });
    }).slice(0, 3).forEach(function (e) {
      var d = document.createElement('div'); d.className = 'lp-def';
      var l = document.createElement('span'); l.className = 'label'; l.textContent = 'What is it?';
      var b = document.createElement('b'); b.textContent = e.t;
      var p = document.createElement('p'); p.textContent = e.d;
      d.appendChild(l); d.appendChild(b); d.appendChild(p); defsEl.appendChild(d);
    });
  }

  function clearAll() {
    input.value = ''; goal = '';
    gcBtn.setAttribute('aria-pressed', 'false'); stBtn.setAttribute('aria-pressed', 'false');
    apply();
  }
  function toResults() {
    var tools = document.querySelector('.lp-tools');
    var y = tools.getBoundingClientRect().top + window.scrollY;
    if (window.scrollY > y + 2 || window.scrollY < y - 2) window.scrollTo({ top: y, behavior: 'smooth' });
  }

  var countEl = document.getElementById('lp-count');
  var timer;
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(apply, 80); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { clearAll(); input.blur(); }
    if (e.key === 'Enter') { input.blur(); toResults(); }
  });
  document.getElementById('lp-clear').addEventListener('click', function () { clearAll(); input.focus(); });
  [gcBtn, stBtn].forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.setAttribute('aria-pressed', btn.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      apply(); toResults();
    });
  });
  goalOn.addEventListener('click', function () { goal = ''; apply(); });
  Array.prototype.slice.call(document.querySelectorAll('[data-goal]')).forEach(function (b) {
    b.addEventListener('click', function () { goal = b.getAttribute('data-goal'); apply(); toResults(); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return;
    var el = document.activeElement, tag = el && el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (el && el.isContentEditable)) return;
    e.preventDefault(); input.focus(); input.select();
  });
  // ?q=... opens the page already searched, so a result can be linked to
  var q0 = new URLSearchParams(location.search).get('q');
  if (q0) { input.value = q0; apply(); }
  window.lpSearch = function (q) { input.value = q; apply(); return Array.prototype.map.call(out.children, function (c) { return c.querySelector('h4').textContent; }); };

  /* section nav highlight + back to top */
  var links = Array.prototype.slice.call(document.querySelectorAll('.lp-nav a'));
  var blocks = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  var topBtn = document.querySelector('.lp-top');
  var tick = false;
  window.addEventListener('scroll', function () {
    if (tick) return; tick = true;
    requestAnimationFrame(function () {
      tick = false;
      topBtn.classList.toggle('show', window.scrollY > 1400);
      var cur = -1;
      for (var i = 0; i < blocks.length; i++) { if (blocks[i] && blocks[i].getBoundingClientRect().top < 160) cur = i; }
      links.forEach(function (a, i) { a.classList.toggle('active', i === cur); });
      if (cur >= 0) { var a = links[cur], nav = a.parentNode; if (a.offsetLeft < nav.scrollLeft || a.offsetLeft + a.offsetWidth > nav.scrollLeft + nav.clientWidth) nav.scrollLeft = a.offsetLeft - 20; }
    });
  }, { passive: true });
  topBtn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
})();
</script>
"""

SEARCH_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
               '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')


def main():
    front, sections = load()
    total = count_tips(sections)

    glossary, goal_list = load_extras()
    EXTRA["rx"], EXTRA["lookup"] = term_pattern(glossary)
    EXTRA["defs"] = {e["id"]: e["def"] for e in glossary}
    EXTRA["glossary"] = glossary
    EXTRA["goal_list"] = goal_list
    EXTRA["goals"] = {g["id"]: g for g in goal_list}
    counts = {}
    for sec in sections:
        for g in sec["groups"]:
            for t in g["tips"]:
                for gid in t.get("goals", []):
                    counts[gid] = counts.get(gid, 0) + 1
    EXTRA["goal_counts"] = counts
    n_src = len({s["url"] for sec in sections for g in sec["groups"] for t in g["tips"] for s in t.get("src", [])})
    n_start = sum(1 for sec in sections for g in sec["groups"] for t in g["tips"] if t.get("lvl") == 1)

    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="noindex">
<style>{page_css()}</style>
</head>
<body>
"""
    hero = f"""<section class="dark lp-hero"><div class="lp-wrap">
  {brand.signature_img()}
  <p class="kicker">Logic Pro Crash Course &middot; Your library &middot; Logic Pro 11 &amp; 12</p>
  <h1>Find the trick for what you&rsquo;re making.</h1>
  <p class="lede">Type what you want to do in your own words, like <em>record vocals</em>, <em>make a beat</em> or
  <em>fix my timing</em>, and the right tricks come up first. New to Logic? <a href="#start">Start here</a>.</p>
  <div class="lp-stats">
    <div class="lp-stat"><span class="label">Tricks</span><b>{total}</b><span>Each one cites its source</span></div>
    <div class="lp-stat"><span class="label">Start here</span><b>{n_start}</b><span>Safe for your first day</span></div>
    <div class="lp-stat"><span class="label">Sources</span><b>{n_src}</b><span>Mostly Apple&rsquo;s own guide</span></div>
  </div>
  <div class="lp-ctas"><a class="pill solid" href="#start">Start here</a><a class="pill" href="#lp-q">Search the tricks</a></div>
</div></section>
"""
    nav = []
    for p in front["pages"]:
        if not p.get("back"):
            nav.append(f'<a href="#{p["id"]}">{esc(p["label"])}</a>')
    for s in sections:
        nav.append(f'<a href="#{slug(s)}"><i>{s["number"]:02d}</i>{esc(s["title"])}</a>')
    for p in front["pages"]:
        if p.get("back"):
            nav.append(f'<a href="#{p["id"]}">{esc(p["label"])}</a>')

    tools = f"""<div class="lp-tools" role="search"><div class="lp-wrap">
  <div class="lp-search">{SEARCH_ICON}
    <label class="visually-hidden" for="lp-q">What do you want to do?</label>
    <input id="lp-q" type="search" autocomplete="off" spellcheck="false" enterkeyhint="search"
      placeholder="What do you want to do? Try: record vocals">
    <span class="lp-slash" aria-hidden="true">/</span>
    <button class="lp-clear" id="lp-clear" type="button">Clear</button>
  </div>
  <button class="lp-goal-on" id="lp-goal-on" type="button" aria-label="Remove goal filter"><span></span> &times;</button>
  <button class="lp-toggle" type="button" id="lp-start" aria-pressed="false">Start here</button>
  <button class="lp-toggle" type="button" id="lp-gc" aria-pressed="false">Game changers</button>
  <span class="visually-hidden" id="lp-count" aria-live="polite"></span>
  <nav class="lp-nav" aria-label="Sections">{"".join(nav)}</nav>
</div></div>
"""
    results = """<section class="paper lp-block lp-results" aria-live="polite"><div class="lp-wrap">
  <p class="kicker">Search results</p>
  <h2 class="sec-title" id="lp-res-title"></h2>
  <p class="lp-hint" id="lp-res-hint"></p>
  <div class="lp-defs" id="lp-defs"></div>
  <div class="lp-tips" id="lp-out"></div>
</div></section>
"""
    book = ['<main class="lp-book">']
    tone = ["paper", "dark"]
    n = 0
    for p in front["pages"]:
        if not p.get("back"):
            book.append(front_block(p, tone[n % 2])); n += 1
    i = 1
    for s in sections:
        chunk, i = section_block(s, i, tone[n % 2]); n += 1
        book.append(chunk)
    for p in front["pages"]:
        if p.get("back"):
            book.append(front_block(p, tone[n % 2])); n += 1
    book.append(f"""<section class="dark lp-end"><div class="lp-wrap">
  <p class="kicker">The end</p>
  <h2 class="sec-title">That&rsquo;s the {total}. Go finish the song.</h2>
  <p class="sec-lede">Come back whenever you get stuck. The search bar is always at the top.</p>
</div></section></main>
""")
    cfg = {
        "stop": STOP, "syn": SYNONYMS,
        "gloss": [{"t": e["term"], "a": e.get("aka", []), "d": e["def"], "id": e["id"]} for e in glossary],
        "goals": {g["id"]: g["label"] for g in goal_list},
    }
    cfg_json = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    foot = f"""<footer class="foot">
  <div>Logic Pro Crash Course &middot; dannny mcccarthy<br>dannnymcccarthy.com &middot; hello@dannnymcccarthy.com</div>
  {brand.signature_img("mark-sig")}
</footer>
<div class="lp-legal"><p>{esc(legal_notice())}</p></div>
<button class="lp-top" type="button">Back to top</button>
<script type="application/json" id="lp-search-cfg">{cfg_json}</script>
"""
    html = head + hero + tools + results + "".join(book) + extra_items(front) + foot + SEARCH_JS + "</body>\n</html>\n"

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course-page.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"Tricks: {total}   Sections: {len(sections)}   Glossary: {len(glossary)}   Goals: {len(counts)}")


if __name__ == "__main__":
    main()
