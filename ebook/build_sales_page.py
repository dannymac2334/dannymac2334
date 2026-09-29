#!/usr/bin/env python3
"""Build the sales page for the Logic Pro Crash Course.

A single self-contained page in the dannny mcccarthy rates design (brand.py):
fonts and signature embedded, nothing loaded from the site.

This page SELLS the book — it does not contain it. The preview cards are
pulled from the real content files rather than retyped, so a copy change in
content/ can never leave a stale claim on the sales page.

Checkout is deliberately not implemented here. The buy buttons point at
/buy, which the site agent wires to a Stripe Checkout session. See HANDOFF.

Output: dist/logic-pro-crash-course-sales.html
"""

import math
import pathlib

import re

import brand
from build import esc, keycap, load, slug, count_tips, sources_html, legal_notice, load_extras

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# The one place the price lives. Shown as a round "$9": round prices read as a
# considered price (as on the rates page), ".99" reads as a discount.
PRICE = "9"
PRICE_USD = f"{float(PRICE):.2f}"   # machine-readable form for Stripe data and JSON-LD
# Sold through the same Gumroad store as the plug-ins. Create the product with this
# exact custom permalink ("logic-pro-crash-course") and nothing else needs to change.
GUMROAD_PERMALINK = "logic-pro-crash-course"
BUY_HREF = f"https://dannnymcccarthy.gumroad.com/l/{GUMROAD_PERMALINK}"
# Read the real page count off the built PDF when it is there, so the sales
# page can never advertise a length the product does not have.
def _pdf_pages(default=84):
    try:
        import pypdfium2
        return len(pypdfium2.PdfDocument(DIST / "logic-pro-crash-course.pdf"))
    except Exception:
        return default

PAGES = _pdf_pages()

# Counts are derived from content/ so the marketing can never outrun the book.
_front, _sections = load()
TRICKS = count_tips(_sections)
# e.g. "Covers Logic Pro 11 and 12" -> "Logic Pro 11 and 12" / "Logic Pro 11 & 12".
# Derived, not typed: a version-scope change in content/00-front.json has to reach the
# sales page, or the page ends up promising support the book does not claim.
VERSIONS = re.sub(r'^Covers\s+', '', _front['edition']).strip()
VERSIONS_SHORT = VERSIONS.replace(' and ', ' &amp; ')
SECTIONS = len(_sections)
TITLE = f"Logic Pro Crash Course — {TRICKS} Tricks | Dannny McCcarthy"
# What one trick costs, rounded UP so the claim is never generous: "under 4¢ a trick".
PER_TRICK = f"under {math.ceil(float(PRICE) * 100 / TRICKS)}¢ a trick"
DESC = (f"{TRICKS} Logic Pro tricks in one clickable PDF. Key commands, editing, mixing and "
        f"workflow across {SECTIONS} sections. ${PRICE}, instant download.")
URL = "https://www.dannnymcccarthy.com/store/logic-pro-crash-course"

# (section number, fragment of the trick title) — resolved against content/
PREVIEW = [
    (4, "Capture the last thing you played"),
    (9, "Make Marquee your ⌘-click tool"),
    (18, "Split any mixed audio into stems"),
    (11, "Give every row a different step rate"),
    (19, "Chord ID reads chords off audio"),
    (12, "Convert a Drummer region to MIDI"),
]

def faq_items(n_start, n_steps, n_gloss):
    return [
    ("Which version of Logic does it cover?",
     f"It works with {VERSIONS}. Every key command is the factory default on a US keyboard, and where a command "
     "could move between versions the book gives the command name and menu path instead. Section 18 covers the "
     "Logic Pro 11 features: Session Players, the Chord track, Stem Splitter, ChromaGlow. Section 19 covers Logic "
     "Pro 12: the Synth Player, Chord ID, and the fact that 12 runs only on Apple silicon."),
    ("I have never used Logic. Is it for me?",
     f"Yes. Start Here walks you through your first session in {n_steps} steps, {n_start} tricks are marked safe for "
     f"your first day, and every Logic word the book uses is explained in plain English in a {n_gloss}-word glossary."),
    ("How do I know the tricks are right?",
     "Every trick shows the source it was checked against, usually Apple's own Logic Pro guide, with a live link. "
     "Anything that could not be confirmed against a source was cut rather than printed on a guess."),
    ("Is this a video course?",
     f"No. It is {TRICKS} written tricks: title, what it does, the key command. Most take ten seconds to read."),
    ("Do I need any third-party plugins?",
     "No. Every trick uses stock Logic Pro. Nothing to buy, nothing to install."),
    ("What exactly do I get?",
     f"Two files. The PDF: {PAGES} pages, clickable contents and bookmarks in the sidebar. The searchable "
     "library: one file you open in any browser, where you type what you want to do (record vocals, make a "
     "beat) and the right tricks come up first. Both are yours to keep and both work offline."),
    ("How is it delivered?",
     "Instantly, through Gumroad, the same store as my plug-ins. You get a download link on screen and "
     "by email as soon as the payment clears."),
    ]


FOR_YOU = [
    "You are brand new to Logic and want to know where to start.",
    "You already know your way around Logic, and keep thinking there must be a faster way to do this.",
    "You lose your thread hunting through menus mid-session.",
    "You have watched hours of tutorials and still cannot remember the one thing you needed.",
    "You want the shortcuts a working producer actually uses, not a feature tour.",
]

NOT_FOR_YOU = [
    "You want a long lesson-by-lesson course rather than short tricks you look up.",
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
    return brand.font_faces() + brand.root_vars() + """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{font-family:var(--font);font-weight:400;line-height:1.5;background:var(--black);color:var(--white)}
a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.wrap{max-width:var(--maxw);margin:0 auto;width:100%}
.section{padding:clamp(64px,12vh,150px) var(--pad)}
.dark{background:var(--black);color:var(--white)}
.paper{background:var(--paper);color:var(--ink)}
.kicker{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.24em;color:var(--kicker);margin-bottom:clamp(20px,4vh,38px)}
.paper .kicker{color:var(--muted-light)}
.hero{padding-top:clamp(72px,14vh,170px)}
.hero h1{font-weight:700;font-size:clamp(38px,8.4vw,140px);line-height:.94;letter-spacing:-.048em;max-width:15ch}
.price-line{margin-top:clamp(24px,4vh,40px);font-size:clamp(16px,1.6vw,22px)}
.price-line b{font-size:1.6em;font-weight:700;letter-spacing:-.03em;margin-right:6px}
.hero .lede{margin-top:clamp(30px,5vh,54px);max-width:56ch;font-size:clamp(16px,1.6vw,22px);color:var(--muted-dark)}
.sec-title{font-weight:700;font-size:clamp(34px,6.4vw,104px);line-height:.96;letter-spacing:-.048em;max-width:18ch}
.sec-lede{margin-top:clamp(20px,3vh,32px);max-width:60ch;font-size:clamp(15px,1.3vw,19px)}
.sec-lede+.sec-lede{margin-top:16px}
.dark .sec-lede{color:var(--muted-dark)}
.paper .sec-lede{color:var(--muted-light)}
.sig{display:block;width:clamp(150px,16vw,230px);height:auto;margin-bottom:clamp(22px,4vh,40px);filter:invert(1)}

/* tier cards, as on the rates page */
.tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(16px,2vw,26px);margin-top:clamp(40px,7vh,90px)}
.combo{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(16px,2vw,26px);margin-top:clamp(40px,7vh,90px)}
.solo{display:grid;grid-template-columns:1fr;margin-top:clamp(40px,7vh,90px)}
.tier{border-radius:16px;padding:clamp(24px,3.4vw,44px);display:flex;flex-direction:column}
.dark .tier{border:1px solid var(--line-dark)}
.paper .tier{border:1px solid var(--line-light)}
.tier .label{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.2em;color:var(--label)}
.paper .tier .label{color:var(--muted-light)}
.tier h3{font-weight:700;font-size:clamp(18px,1.8vw,24px);margin-top:10px;line-height:1.2;letter-spacing:-.02em}
.tier .amount{font-weight:700;font-size:clamp(38px,4.4vw,64px);line-height:1;letter-spacing:-.03em;margin:clamp(18px,2.6vh,28px) 0 4px;font-variant-numeric:tabular-nums}
.tier .terms{font-size:13px;color:var(--label)}
.paper .tier .terms{color:var(--muted-light)}
.tier .who{margin-top:clamp(16px,2.4vh,24px);font-size:15px}
.dark .tier .who{color:var(--muted-dark)}
.paper .tier .who{color:var(--muted-light)}
.tier ul{list-style:none;margin-top:auto;padding-top:clamp(20px,3vh,30px)}
.dark .tier ul{border-top:1px solid var(--line-dark)}
.paper .tier ul{border-top:1px solid var(--line-light)}
.tier li{font-size:14px;padding:6px 0 6px 18px;position:relative}
.dark .tier li{color:var(--muted-dark)}
.paper .tier li{color:var(--muted-light)}
.tier li::before{content:"";position:absolute;left:0;top:.95em;width:8px;height:1px;background:currentColor;opacity:.5}
.solo .tier ul{columns:2;column-gap:clamp(24px,3vw,44px)}
.solo .tier li{break-inside:avoid}
.tier .keys{margin-top:16px;display:flex;gap:6px;flex-wrap:wrap}
.tier .src{margin-top:auto;padding-top:14px;border-top:1px solid var(--line-light);font-size:12px;line-height:1.5;color:var(--muted-light)}
.dark .tier .src{border-color:var(--line-dark);color:var(--label)}
.tier .src span{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;margin-right:6px}
.tier .src a{text-decoration:underline;text-underline-offset:2px}
/* whatever comes before a divider keeps clear of it, however tall the card */
.tier h3:has(+ ul),.tier .who:has(+ ul),.tier .who:has(+ .src),.tier .keys:has(+ .src){margin-bottom:22px}
.kbd{display:inline-block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;border-radius:100px;padding:.4rem .85rem;white-space:nowrap}
.dark .kbd{background:#fff;color:#000}
.paper .kbd{background:var(--ink);color:#fff}
.kbd-phrase{background:transparent !important;color:inherit !important;border:1px solid currentColor}

/* terms-style lists */
.tlist{margin-top:clamp(40px,7vh,90px);display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(24px,3vw,44px)}
.tlist section h4{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.2em;padding-bottom:12px;margin-bottom:12px}
.paper .tlist section h4{border-bottom:1px solid var(--line-light)}
.dark .tlist section h4{border-bottom:1px solid var(--line-dark)}
.tlist section p{font-size:15px}
.paper .tlist section p{color:var(--muted-light)}
.dark .tlist section p{color:var(--muted-dark)}
.index{margin-top:clamp(40px,7vh,90px);display:grid;grid-template-columns:repeat(3,1fr);gap:0 clamp(24px,3vw,44px)}
.index div{display:flex;align-items:baseline;gap:14px;padding:14px 0;border-bottom:1px solid var(--line-light)}
.index i{font-style:normal;font-size:12px;font-weight:600;letter-spacing:.14em;color:var(--muted-light);min-width:1.8rem;font-variant-numeric:tabular-nums}
.index b{flex:1;font-size:17px;letter-spacing:-.02em;line-height:1.25}
.index em{font-style:normal;font-size:13px;color:var(--muted-light);white-space:nowrap}

.pill{display:inline-flex;align-items:center;justify-content:center;padding:20px 46px;border:2px solid currentColor;border-radius:100px;
  font-weight:500;text-transform:uppercase;letter-spacing:.24em;font-size:12px;
  transition:background .35s var(--ease),color .35s var(--ease),transform .35s var(--ease);margin-top:clamp(30px,5vh,54px)}
.dark .pill:hover{background:#fff;color:#000}
.paper .pill:hover{background:#000;color:#fff}
.pill:active{transform:scale(.97)}
.pill.solid{background:#fff;color:#000;border-color:#fff}
.dark .pill.solid:hover{background:transparent;color:#fff}

.foot{padding:clamp(40px,7vh,80px) var(--pad);border-top:1px solid var(--line-dark);display:flex;justify-content:space-between;
  align-items:flex-end;gap:24px;flex-wrap:wrap;font-size:13px;color:var(--kicker)}
.foot .mark-sig{display:block;width:150px;height:auto;filter:invert(1)}
.legal{padding:0 var(--pad) 40px;font-size:11px;line-height:1.6;color:var(--kicker)}
.legal p{max-width:var(--maxw);margin:0 auto}

@media(max-width:900px){
  .tiers,.combo,.tlist,.index{grid-template-columns:1fr}
  .solo .tier ul{columns:1}
}
"""


def preview_card(sec, tip, i):
    o = ['<article class="tier">', f'<div class="label">Section {sec["number"]:02d} &middot; {esc(sec["title"])}</div>',
         f'<h3>{esc(tip["t"])}</h3>', f'<p class="who">{esc(tip["d"])}</p>']
    if tip.get("k"):
        o.append(f'<div class="keys">{keycap(tip["k"])}</div>')
    if tip.get("src"):
        o.append(sources_html(tip["src"], cls="src"))
    o.append("</article>")
    return "".join(o)


def buy(label, cls="pill solid"):
    return (f'<a class="{cls}" href="{BUY_HREF}" data-product="logic-pro-crash-course" '
            f'data-price-usd="{PRICE_USD}">{label}</a>')


def main():
    front, sections = load()
    total = count_tips(sections)
    previews = find_preview(sections)
    glossary, goals = load_extras()
    n_start = sum(1 for s in sections for g in s["groups"] for t in g["tips"] if t.get("lvl") == 1)
    n_steps = sum(len(p.get("steps", [])) for p in front["pages"])

    index_rows = "".join(
        f'<div><i>{s["number"]:02d}</i><b>{esc(s["title"])}</b>'
        f'<em>{sum(len(g["tips"]) for g in s["groups"])} tricks</em></div>'
        for s in sections)
    faq = "".join(f"<section><h4>{esc(q)}</h4><p>{esc(a)}</p></section>" for q, a in faq_items(n_start, n_steps, len(glossary)))
    yes = "".join(f"<li>{esc(x)}</li>" for x in FOR_YOU)
    no = "".join(f"<li>{esc(x)}</li>" for x in NOT_FOR_YOU)
    cards = "".join(preview_card(s, t, i + 1) for i, (s, t) in enumerate(previews))
    inside = [
        f"{total} tricks, each citing the source it was checked against",
        f"Start Here: {n_steps} first steps for someone who has never opened Logic",
        f"{n_start} tricks marked Start Here, safe for your first day",
        f"I Want To…: {len(goals)} goals, from making a beat to exporting a song",
        f"A glossary of {len(glossary)} Logic words in plain English",
        "The searchable library: one file, works offline, finds tricks by what you want to do",
        "Clickable contents and PDF bookmarks on every section",
        f"Covers {VERSIONS}",
        "Stock Logic Pro only, no plug-ins to buy",
    ]
    inside_li = "".join(f"<li>{esc(x)}</li>" for x in inside)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="dannny mcccarthy">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<link rel="canonical" href="{URL}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Product","name":"Logic Pro Crash Course","description":"{DESC}","brand":{{"@type":"Brand","name":"dannny mcccarthy"}},"offers":{{"@type":"Offer","price":"{PRICE_USD}","priceCurrency":"USD","availability":"https://schema.org/InStock","url":"{URL}"}}}}
</script>
<style>{sales_css()}</style>
</head>
<body>

<section class="section dark hero">
  <div class="wrap">
    {brand.signature_img()}
    <div class="kicker">Logic Pro Crash Course &middot; Digital download &middot; {VERSIONS_SHORT}</div>
    <h1>Logic can already do it. Here is where it lives.</h1>
    <p class="lede">{total} tricks that actually work, in one clickable PDF you keep open while you produce.
    Brand new to Logic? It starts from zero. Every trick cites its source.</p>
    <p class="price-line"><b>${PRICE}</b> for all {total} &middot; {PER_TRICK} &middot; one payment</p>
    {buy(f"Get it for ${PRICE}")}
  </div>
</section>

<section class="section paper">
  <div class="wrap">
    <div class="kicker">The problem</div>
    <h2 class="sec-title">It is not a skill problem. It is a lookup problem.</h2>
    <p class="sec-lede">You are three hours into a session, the idea is finally working, and you stop, because you
    know Logic can do the thing you need and you cannot remember how. So you open a browser, watch four minutes of
    somebody clearing their throat, find the answer, and come back. The idea has gone cold.</p>
    <p class="sec-lede">This book is the lookup. {total} tricks sorted into {len(sections)} sections, each short enough
    to read in ten seconds and use straight away, plus an index that finds them by what you are trying to make.</p>
    <div class="solo">
      <article class="tier">
        <div class="label">Digital download</div>
        <h3>Logic Pro Crash Course</h3>
        <div class="amount">${PRICE}</div>
        <div class="terms">One payment &middot; {PER_TRICK} &middot; {PAGES} pages &middot; yours to keep</div>
        <p class="who">The PDF and the searchable library, delivered the moment your payment clears. Built to sit open on a second screen while you work.</p>
        <ul>{inside_li}</ul>
      </article>
    </div>
  </div>
</section>

<section class="section dark">
  <div class="wrap">
    <div class="kicker">A few of them</div>
    <h2 class="sec-title">Six tricks, free, right now.</h2>
    <p class="sec-lede">Taken straight from the book, sources and all. If these are new to you, the other {total - len(previews)} will be too.</p>
    <div class="tiers">{cards}</div>
  </div>
</section>

<section class="section paper">
  <div class="wrap">
    <div class="kicker">What&rsquo;s inside</div>
    <h2 class="sec-title">{len(sections)} sections. {total} tricks.</h2>
    <p class="sec-lede">Organised by what you are doing, not by which menu it lives in, so you can find the right one mid-project.</p>
    <div class="index">{index_rows}</div>
  </div>
</section>

<section class="section dark">
  <div class="wrap">
    <div class="kicker">Honestly</div>
    <h2 class="sec-title">Who this is for, and who it isn&rsquo;t.</h2>
    <div class="combo">
      <article class="tier"><div class="label">Get it if</div><h3>You want answers, fast.</h3><ul>{yes}</ul></article>
      <article class="tier"><div class="label">Skip it if</div><h3>You want something else.</h3><ul>{no}</ul></article>
    </div>
  </div>
</section>

<section class="section paper">
  <div class="wrap">
    <div class="kicker">Questions</div>
    <h2 class="sec-title">Before you buy.</h2>
    <div class="tlist">{faq}</div>
  </div>
</section>

<section class="section dark">
  <div class="wrap">
    <div class="kicker">Logic Pro Crash Course</div>
    <h2 class="sec-title">Get the {total}.</h2>
    <p class="sec-lede">${PRICE}, one payment, {PER_TRICK}. The {PAGES}-page PDF and the searchable library, delivered the moment your payment clears.</p>
    {buy(f"Get it for ${PRICE}")}
  </div>
</section>

<footer class="foot">
  <div>dannny mcccarthy &middot; Strategy &middot; Brand identity &middot; Websites &middot; Brand sound<br>
  dannnymcccarthy.com &middot; hello@dannnymcccarthy.com</div>
  {brand.signature_img("mark-sig")}
</footer>
<div class="legal"><p>{esc(legal_notice())}</p></div>
</body>
</html>
"""

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course-sales.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"Price ${PRICE} ({PER_TRICK})   Preview cards: {len(previews)}   Buy href: {BUY_HREF}")


if __name__ == "__main__":
    main()
