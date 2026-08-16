#!/usr/bin/env python3
"""Build the sales page for the Logic Pro Crash Course.

A drop-in page for dannnymcccarthy.com, same as build_site_page.py: it links
the site's own css/style.css and js/main.js, carries the site header and
footer, and uses the site's .reveal classes for animation.

This page SELLS the book — it does not contain it. The preview cards are
pulled from the real content files rather than retyped, so a copy change in
content/ can never leave a stale claim on the sales page.

Checkout is deliberately not implemented here. The buy buttons point at
/buy, which the site agent wires to a Stripe Checkout session. See HANDOFF.

Output: dist/logic-pro-crash-course-sales.html
"""

import pathlib

from build import esc, keycap, load, slug, count_tips
from build_site_page import FOOTER, SITE_NAV, page_css

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

PRICE = "14.99"
BUY_HREF = "/buy"
PAGES = 82

TITLE = "Logic Pro Crash Course — 355 Tricks | Dannny McCcarthy"
DESC = ("355 Logic Pro tricks in one clickable PDF. Key commands, editing, mixing and "
        f"workflow across 19 sections. ${PRICE}, instant download.")
URL = "https://www.dannnymcccarthy.com/logic-pro-crash-course"

# (section number, fragment of the trick title) — resolved against content/
PREVIEW = [
    (4, "Capture the last thing you played"),
    (9, "Click any region after marqueeing"),
    (18, "Split any mixed audio into four parts"),
    (11, "Give every row a different step rate"),
    (1, "Run two buffer sizes"),
    (12, "Set the Follow parameter"),
]

FAQ = [
    ("Which version of Logic does it cover?",
     "It works with Logic Pro 10.7, 11 and 12. Every key command is the factory default on a "
     "US keyboard, and where a command could move between versions the book gives the exact "
     "command name and menu path instead, so it stays correct. To be straight with you: Section 18 covers the Logic Pro 11 features in depth — Session Players, the Chord track, Stem Splitter, ChromaGlow. Section 19 is an upgrade playbook for handling any major release, not a feature-by-feature tour of Logic Pro 12."),
    ("Is this a video course?",
     "No. It is 355 written tricks: title, what it does, the key command. Most take ten "
     "seconds to read. It is built to sit open on a second screen while you work, not to be "
     "watched."),
    ("Do I need any third-party plugins?",
     "No. Every trick uses stock Logic Pro. Nothing to buy, nothing to install."),
    ("I am fairly new to Logic. Is it too advanced?",
     "The early sections are settings and fundamentals — the things worth fixing before you "
     "record a note. It gets deeper from there. You should be comfortable opening a project "
     "and recording a track; you do not need to be an expert."),
    ("What exactly do I get?",
     f"One PDF, {PAGES} pages, full colour. Clickable contents, bookmarks in the sidebar, and "
     "it opens on any device. It is yours to keep and it works offline."),
    ("How is it delivered?",
     "Instantly. You get a download link as soon as the payment clears."),
]

FOR_YOU = [
    "You already know your way around Logic, and keep thinking there must be a faster way to do this.",
    "You lose your thread hunting through menus mid-session.",
    "You have watched hours of tutorials and still cannot remember the one thing you needed.",
    "You want the shortcuts a working producer actually uses, not a feature tour.",
]

NOT_FOR_YOU = [
    "You have never opened Logic Pro and need a from-scratch beginner course.",
    "You want video walkthroughs rather than something to reference quickly.",
    "You are looking for mixing theory or a genre-specific production course.",
]


def find_preview(sections):
    by_num = {s["number"]: s for s in sections}
    out = []
    for num, frag in PREVIEW:
        sec = by_num[num]
        for g in sec["groups"]:
            for t in g["tips"]:
                if frag.lower() in t["t"].lower():
                    out.append((sec, t))
                    break
    missing = len(PREVIEW) - len(out)
    if missing:
        print(f"  WARN  {missing} preview trick(s) not found — check PREVIEW against content/")
    return out


def sales_css():
    return """
/* ---- sales page additions ---- */
.lp-price{display:flex;align-items:baseline;justify-content:center;gap:12px;margin-top:34px}
.lp-price b{font-size:clamp(38px,6vw,64px);font-weight:700;letter-spacing:-.04em;line-height:1}
.lp-price span{font-size:11px;font-weight:500;letter-spacing:.2em;text-transform:uppercase;opacity:.55}
.pill.solid{background:#fff;color:#000;border-color:#fff}
.pill.solid:hover{background:transparent;color:#fff;border-color:#fff}
.lp-trust{margin:22px auto 0;font-size:11px;font-weight:500;letter-spacing:.14em;
  text-transform:uppercase;color:#8a8a86}
.lp-trust span{white-space:nowrap}
.lp-trust i{font-style:normal;opacity:.4;padding:0 10px}

.lp-sec{padding:clamp(64px,11vh,130px) var(--pad);border-top:1px solid var(--line-dark)}
.lp-sec-inner{max-width:1100px;margin:0 auto}
.lp-h2{font-size:clamp(30px,5.6vw,76px);letter-spacing:-.025em;line-height:.96;
  text-transform:uppercase;margin:14px 0 0;max-width:20ch}
.lp-sec .lp-intro{margin-top:26px}

.lp-cols{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,4vw,56px);margin-top:44px}
@media(max-width:820px){.lp-cols{grid-template-columns:1fr}}
.lp-col h3{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.16em;
  margin:0 0 18px;padding-bottom:14px;border-bottom:1px solid var(--line-dark)}
.lp-col ul{margin:0;padding:0;list-style:none}
.lp-col li{position:relative;padding:12px 0 12px 30px;font-size:15px;line-height:1.6;color:var(--lp-dim)}
.lp-col li::before{content:"";position:absolute;left:0;top:1.35em;width:14px;height:1px;
  background:currentColor;opacity:.5}
.lp-col.no li{opacity:.62}

/* section index — proves the scope without giving it away */
.lp-index{margin-top:44px;border-top:1px solid var(--line-dark)}
.lp-index div{display:flex;align-items:baseline;gap:clamp(12px,2vw,28px);padding:14px 0;
  border-bottom:1px solid var(--line-dark)}
.lp-index i{font-style:normal;font-size:11px;font-weight:600;letter-spacing:.14em;opacity:.4;
  min-width:2rem;font-variant-numeric:tabular-nums}
.lp-index b{flex:1;font-size:clamp(15px,2vw,24px);font-weight:700;text-transform:uppercase;
  letter-spacing:-.015em}
.lp-index em{font-style:normal;font-size:10px;font-weight:500;letter-spacing:.16em;
  text-transform:uppercase;opacity:.5;white-space:nowrap;font-variant-numeric:tabular-nums}

.lp-faq{margin-top:44px;border-top:1px solid var(--line-dark)}
.lp-faq details{border-bottom:1px solid var(--line-dark)}
.lp-faq summary{cursor:pointer;list-style:none;padding:20px 40px 20px 0;position:relative;
  font-size:clamp(15px,1.8vw,20px);font-weight:600;letter-spacing:-.01em}
.lp-faq summary::-webkit-details-marker{display:none}
.lp-faq summary::after{content:"+";position:absolute;right:6px;top:50%;transform:translateY(-50%);
  font-size:22px;font-weight:400;opacity:.5;transition:transform .3s var(--ease)}
.lp-faq details[open] summary::after{transform:translateY(-50%) rotate(45deg)}
.lp-faq p{margin:0;padding:0 40px 24px 0;font-size:15px;line-height:1.7;color:var(--lp-dim);
  max-width:70ch}

.lp-final{text-align:center;padding:clamp(70px,13vh,150px) var(--pad);border-top:1px solid var(--line-dark)}
.lp-final .lp-h2{margin-left:auto;margin-right:auto}
.lp-note{margin:26px auto 0;max-width:52ch;font-size:13px;line-height:1.7;color:#8a8a86}
"""


def preview_card(sec, tip, i):
    keys = tip.get("k")
    cls = "lp-tip reveal" + ("" if keys else " no-keys") + (
        " is-key" if tip.get("b") else "")
    o = [f'<article class="{cls}">', '<div class="lp-tip-head">',
         f'<span class="lp-num">{i:03d}</span>',
         f'<span class="lp-badge">Section {sec["number"]:02d}</span>', "</div>",
         f'<h4>{esc(tip["t"])}</h4>', f'<p>{esc(tip["d"])}</p>']
    if keys:
        k = keycap(keys).replace('class="kbd kbd-phrase"', 'class="lp-kbd phrase"')
        k = k.replace('class="kbd"', 'class="lp-kbd"')
        o.append(f'<div class="lp-keys">{k}</div>')
    o.append("</article>")
    return "".join(o)


def buy(label, cls="pill solid"):
    return (f'<a class="{cls}" href="{BUY_HREF}" data-product="logic-pro-crash-course" '
            f'data-price-usd="{PRICE}">{label}</a>')


def main():
    front, sections = load()
    total = count_tips(sections)
    previews = find_preview(sections)

    index_rows = "".join(
        f'<div><i>{s["number"]:02d}</i><b>{esc(s["title"])}</b>'
        f'<em>{sum(len(g["tips"]) for g in s["groups"])} tricks</em></div>'
        for s in sections
    )
    faq = "".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ
    )
    yes = "".join(f"<li>{esc(x)}</li>" for x in FOR_YOU)
    no = "".join(f"<li>{esc(x)}</li>" for x in NOT_FOR_YOU)
    cards = "".join(preview_card(s, t, i + 1) for i, (s, t) in enumerate(previews))

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Dannny McCcarthy">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<link rel="canonical" href="{URL}">
<meta property="og:image" content="https://www.dannnymcccarthy.com/assets/brand/og-cover.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="600">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="https://www.dannnymcccarthy.com/assets/brand/og-cover.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<script defer src="js/main.js"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Product","name":"Logic Pro Crash Course","description":"{DESC}","image":"https://www.dannnymcccarthy.com/assets/brand/og-cover.jpg","brand":{{"@type":"Brand","name":"Dannny McCcarthy"}},"offers":{{"@type":"Offer","price":"{PRICE}","priceCurrency":"USD","availability":"https://schema.org/InStock","url":"{URL}"}}}}
</script>
<style>{page_css()}{sales_css()}</style>
<noscript><style>.lp .reveal{{opacity:1 !important;transform:none !important}}</style></noscript>
</head>
<body>
<header class="site-head" data-header>
  <a href="index.html" aria-label="Home">
    <img class="logo white" src="assets/brand/DM_WHITE.png" alt="Dannny McCcarthy">
    <img class="logo black" src="assets/brand/DM_BLACK.png" alt="Dannny McCcarthy">
  </a>
  {SITE_NAV}
</header>

<section class="proj lp">

  <div class="lp-hero">
    <p class="lp-eyebrow reveal">Logic Pro &middot; Digital download</p>
    <h1 class="reveal d1">Logic Pro<br>Crash Course</h1>
    <p class="lp-lead reveal d1">{total} tricks that actually work — the ones nobody tells you,
    in one clickable PDF you keep open while you produce. No long tutorials. No fluff.</p>
    <div class="lp-price reveal d2"><b>${PRICE}</b><span>One payment &middot; Yours to keep</span></div>
    <div class="lp-cta reveal d2">{buy("Get instant access")}</div>
    <p class="lp-trust reveal d3"><span>{PAGES} pages</span><i>&middot;</i>
      <span>Instant download</span><i>&middot;</i><span>Logic Pro 10.7, 11 &amp; 12</span></p>
  </div>

  <div class="lp-sec"><div class="lp-sec-inner">
    <p class="lp-eyebrow reveal">The problem</p>
    <h2 class="lp-h2 reveal">Logic can already do it. You just can&rsquo;t remember where it lives.</h2>
    <p class="lp-intro reveal">You are three hours into a session, the idea is finally working, and
    you stop — because you know Logic can do the thing you need and you cannot remember how. So you
    open a browser, watch four minutes of somebody clearing their throat, find the answer, and come
    back. The idea has gone cold.</p>
    <p class="lp-intro reveal">That is not a skill problem. It is a lookup problem. Logic Pro has
    over two thousand commands, and the useful ones are buried three menus deep or sitting on a
    key nobody mentions.</p>
    <p class="lp-intro reveal">This book is the lookup. {total} tricks, sorted into {len(sections)}
    sections, each one short enough to read in ten seconds and use immediately.</p>
  </div></div>

  <div class="lp-sec"><div class="lp-sec-inner">
    <p class="lp-eyebrow reveal">A few of them</p>
    <h2 class="lp-h2 reveal">Six tricks, free, right now.</h2>
    <p class="lp-intro reveal">Taken straight from the book. If these are new to you, the other
    {total - len(previews)} will be too.</p>
    <div class="lp-tips" style="margin-top:40px">{cards}</div>
  </div></div>

  <div class="lp-sec"><div class="lp-sec-inner">
    <p class="lp-eyebrow reveal">What&rsquo;s inside</p>
    <h2 class="lp-h2 reveal">{len(sections)} sections. {total} tricks.</h2>
    <p class="lp-intro reveal">Organised by what you are doing, not by what menu it lives in — so
    you can find the right one mid-project without breaking your flow.</p>
    <div class="lp-index reveal">{index_rows}</div>
  </div></div>

  <div class="lp-sec"><div class="lp-sec-inner">
    <p class="lp-eyebrow reveal">Honestly</p>
    <h2 class="lp-h2 reveal">Who this is for, and who it isn&rsquo;t.</h2>
    <div class="lp-cols">
      <div class="lp-col reveal"><h3>Get it if</h3><ul>{yes}</ul></div>
      <div class="lp-col no reveal d1"><h3>Skip it if</h3><ul>{no}</ul></div>
    </div>
  </div></div>

  <div class="lp-sec"><div class="lp-sec-inner">
    <p class="lp-eyebrow reveal">Questions</p>
    <h2 class="lp-h2 reveal">Before you buy.</h2>
    <div class="lp-faq reveal">{faq}</div>
  </div></div>

  <div class="lp-final">
    <h2 class="lp-h2 reveal">Get the {total}.</h2>
    <div class="lp-price reveal d1"><b>${PRICE}</b><span>One payment &middot; Yours to keep</span></div>
    <div class="lp-cta reveal d1">{buy("Get instant access")}</div>
    <p class="lp-note reveal d2">A single PDF, {PAGES} pages, delivered the moment your payment
    clears. Every key command in it is the Logic Pro factory default; where a command could move
    between versions, the book gives the command name and menu path so it stays correct.</p>
  </div>

</section>
{FOOTER}
</body>
</html>
"""

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course-sales.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"Price ${PRICE}   Preview cards: {len(previews)}   Buy href: {BUY_HREF}")


if __name__ == "__main__":
    main()
