#!/usr/bin/env python3
"""Build the eBook as a drop-in page for dannnymcccarthy.com.

Unlike build.py — which emits a standalone document with everything inlined —
this emits a page that belongs to the site: it links the site's own
`css/style.css` and `js/main.js`, carries the site header and footer verbatim,
and uses the site's `.reveal` classes so the existing IntersectionObserver in
main.js animates it with no new code.

Only the components the site does not already have (trick cards, the contents
list, the key tables and the sticky section nav) are styled here, scoped under
`.lp` so nothing can leak into the rest of the site.

Output: dist/logic-pro-crash-course-page.html
Drop it at the ROOT of the site repo, next to work.html — the relative
`css/` and `js/` paths depend on that.
"""

import pathlib

from build import esc, keycap, load, slug, count_tips

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

PDF_HREF = "assets/resources/logic-pro-crash-course.pdf"
HIGHLIGHT = "GAME CHANGER"

TITLE = "Logic Pro Crash Course | Dannny McCcarthy"
DESC = ("355 Logic Pro tricks across 19 sections — key commands, editing, mixing and "
        "workflow. A free resource from Seattle designer and producer Dannny McCcarthy.")
URL = "https://www.dannnymcccarthy.com/logic-pro-crash-course"

SITE_NAV = (
    '<nav class="nav"><a href="index.html">Home</a><a href="work.html">Work</a>'
    '<a href="maccaroni.html">Maccaroni</a><a href="services.html">Work with me</a>'
    '<a href="contact.html">Contact</a></nav>'
)


def head():
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta property="og:type" content="article">
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
<style>{page_css()}</style>
<noscript><style>
/* The site hides .reveal elements until main.js observes them. On a page that
   is almost entirely .reveal content, a blocked script would leave it blank,
   so opt out of the animation when there is no JS to finish it. */
.lp .reveal{{opacity:1 !important;transform:none !important}}
.lp-nav{{display:none}}
</style></noscript>
</head>
<body>
<header class="site-head" data-header>
  <a href="index.html" aria-label="Home">
    <img class="logo white" src="assets/brand/DM_WHITE.png" alt="Dannny McCcarthy">
    <img class="logo black" src="assets/brand/DM_BLACK.png" alt="Dannny McCcarthy">
  </a>
  {SITE_NAV}
</header>
"""


def page_css():
    return """
/* ===== Logic Pro Crash Course — page-only styles =====
   Everything is scoped under .lp. Colours, type, easing and the glass rim all
   come from the site's own tokens so this page cannot drift from the rest. */
.lp{--lp-card:#171922;--lp-dim:#d5d4cf}
.lp .lp-hero{padding:clamp(130px,20vh,220px) var(--pad) clamp(40px,7vh,72px);text-align:center;
  border-bottom:1px solid var(--line-dark)}
.lp .lp-hero h1{font-size:clamp(38px,7.5vw,110px);letter-spacing:-.035em;line-height:.92;
  text-transform:uppercase;margin:18px 0 0}
.lp .lp-lead{margin:24px auto 0;max-width:60ch;font-size:clamp(15px,1.3vw,19px);line-height:1.6;color:var(--lp-dim)}
.lp .lp-stats{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:34px}
.lp .lp-stat{border:1px solid var(--line-dark);border-radius:100px;padding:13px 28px;min-width:120px}
.lp .lp-stat b{display:block;font-size:24px;line-height:1;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.lp .lp-stat span{display:block;margin-top:6px;font-size:10px;font-weight:500;letter-spacing:.2em;
  text-transform:uppercase;opacity:.6}
.lp .lp-cta{margin-top:38px}

/* sticky section nav — same behaviour language as the site's other jump bars */
.lp-nav{position:sticky;top:56px;z-index:90;padding:11px var(--pad);box-sizing:border-box;
  background:rgba(0,0,0,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
  border-top:1px solid var(--line-dark);border-bottom:1px solid var(--line-dark)}
.lp-nav-inner{--fade:32px;max-width:1200px;margin:0 auto;display:flex;gap:8px;overflow-x:auto;
  overscroll-behavior-x:contain;touch-action:pan-x;-webkit-overflow-scrolling:touch;cursor:grab;
  scrollbar-width:none;-ms-overflow-style:none;
  -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 var(--fade),#000 calc(100% - var(--fade)),transparent 100%);
          mask-image:linear-gradient(90deg,transparent 0,#000 var(--fade),#000 calc(100% - var(--fade)),transparent 100%)}
.lp-nav-inner::-webkit-scrollbar{display:none}
.lp-nav-inner.dragging{cursor:grabbing}
.lp-nav-inner a{flex:0 0 auto;display:inline-flex;align-items:center;gap:7px;padding:7px 15px;
  border:1px solid #3a3a3a;border-radius:100px;font-size:11px;font-weight:500;letter-spacing:.11em;
  text-transform:uppercase;color:#e8e8e6;white-space:nowrap;
  transition:background .25s var(--ease),border-color .25s var(--ease),color .25s var(--ease)}
.lp-nav-inner a i{font-style:normal;opacity:.45;font-variant-numeric:tabular-nums}
.lp-nav-inner a:hover{background:#141414;border-color:#5a5a5a;color:#fff}
.lp-nav-inner a.active{background:#fff;border-color:#fff;color:#000}
.lp-nav-inner a.active i{opacity:.5}

.lp-body{max-width:1200px;margin:0 auto;padding:clamp(50px,9vh,100px) var(--pad) 0}
.lp-block{scroll-margin-top:140px;margin-bottom:clamp(60px,11vh,130px)}
.lp-block-head{border-bottom:1px solid var(--line-dark);padding-bottom:18px;margin-bottom:34px}
.lp-eyebrow{font-weight:600;text-transform:uppercase;letter-spacing:.24em;font-size:11px;opacity:.55;margin:0}
.lp-block-head h2{font-size:clamp(30px,5.4vw,72px);letter-spacing:-.02em;line-height:.95;
  text-transform:uppercase;margin:14px 0 0}
.lp-count{display:inline-block;margin-top:16px;border:1px solid var(--line-dark);border-radius:100px;
  padding:6px 16px;font-size:10px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;opacity:.7}
.lp-intro{max-width:68ch;font-size:clamp(15px,1.2vw,18px);line-height:1.7;color:var(--lp-dim);margin:0 0 8px}
/* Front-matter blocks have no card grid, so hold every element to one measure
   instead of letting prose sit narrow while callouts run the full width. */
.lp-doc .lp-intro,.lp-doc .lp-rules,.lp-doc .lp-legend,.lp-doc .lp-table,
.lp-doc .lp-callout,.lp-doc .lp-sub{max-width:900px}

.lp-group{margin-top:clamp(34px,5.5vh,58px)}
.lp-group-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  border-bottom:1px solid var(--line-dark);padding-bottom:12px;margin-bottom:20px}
.lp-group-head h3{font-size:clamp(15px,1.5vw,19px);font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;line-height:1.2;margin:0}
.lp-path{margin:0;font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.14em;
  border:1px solid var(--line-dark);border-radius:100px;padding:5px 13px;opacity:.7}
.lp-note{margin:0 0 18px;font-size:13px;color:#8a8a86}

.lp-tips{display:grid;grid-template-columns:repeat(auto-fill,minmax(20rem,1fr));gap:18px}

/* the site's liquid-glass rim, applied to a text card instead of an image */
.lp-tip{position:relative;border-radius:16px;padding:1px;display:flex;flex-direction:column;
  background:
    linear-gradient(135deg,rgba(255,255,255,.9) 0%,rgba(255,255,255,.28) 16%,rgba(255,255,255,.08) 42%,
      rgba(255,255,255,.08) 60%,rgba(255,255,255,.3) 82%,rgba(255,255,255,.8) 100%),
    linear-gradient(0deg,var(--lp-card),var(--lp-card));
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.22),0 0 0 1px rgba(255,255,255,.1),
    0 20px 44px -24px rgba(0,0,0,.7),0 4px 14px -10px rgba(0,0,0,.55);
  transition:box-shadow .5s var(--ease),transform .5s var(--ease)}
.lp-tip::before{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;border-radius:16px;
  padding:1px;
  background:linear-gradient(120deg,rgba(255,255,255,0) 38%,rgba(255,255,255,.9) 50%,rgba(255,255,255,0) 62%);
  background-size:260% 100%;background-position:100% 0;
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
  -webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
  mask-composite:exclude;opacity:0;
  transition:opacity .5s var(--ease),background-position .9s var(--ease)}
.lp-tip:hover::before{opacity:1;background-position:0 0}
.lp-tip:hover{transform:translateY(-3px);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.4),0 0 0 1px rgba(255,255,255,.2),
    0 0 22px -2px rgba(220,230,255,.32),0 24px 48px -22px rgba(0,0,0,.7)}
.lp-tip>*{position:relative;z-index:2;background:var(--lp-card)}
.lp-tip-head{display:flex;align-items:center;gap:11px;padding:20px 22px 0;border-radius:15px 15px 0 0}
.lp-tip h4{margin:0;padding:11px 22px 0;font-size:16px;font-weight:600;letter-spacing:-.01em;
  line-height:1.3;text-transform:none}
.lp-tip p{margin:0;padding:9px 22px 0;font-size:13.5px;line-height:1.65;color:var(--lp-dim);flex:1}
.lp-keys{padding:16px 22px 20px;border-radius:0 0 15px 15px;margin-top:auto}
.lp-tip.no-keys p{padding-bottom:22px;border-radius:0 0 15px 15px}
.lp-num{font-size:11px;font-weight:600;letter-spacing:.14em;opacity:.45;font-variant-numeric:tabular-nums}
.lp-badge{font-size:9px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;border-radius:100px;
  padding:4px 11px;background:#fff;color:#000}
.lp-tip.is-key{box-shadow:inset 0 0 0 1px rgba(255,255,255,.45),0 0 0 1px rgba(255,255,255,.2),
  0 20px 44px -24px rgba(0,0,0,.7)}

.lp-kbd{display:inline-block;font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  background:#fff;color:#000;border-radius:100px;padding:.34rem .8rem;white-space:nowrap}
.lp-kbd.phrase{background:transparent;color:#fff;border:1px solid var(--line-dark);letter-spacing:.08em}

/* front-matter blocks */
.lp-rules{margin:0;padding:0;list-style:none}
.lp-rules li{padding:15px 0 15px 30px;border-bottom:1px solid var(--line-dark);position:relative;
  color:var(--lp-dim);font-size:15px;line-height:1.6;max-width:74ch}
.lp-rules li:first-child{border-top:1px solid var(--line-dark)}
.lp-rules li::before{content:"";position:absolute;left:0;top:1.5em;width:14px;height:1px;
  background:currentColor;opacity:.5}
.lp-legend{margin:0}
.lp-legend div{display:grid;grid-template-columns:14rem minmax(0,1fr);gap:1.2rem;align-items:baseline;
  padding:15px 0;border-bottom:1px solid var(--line-dark)}
.lp-legend div:first-child{border-top:1px solid var(--line-dark)}
.lp-legend dt{display:flex;align-items:baseline;gap:1rem}
.lp-sym{font-size:26px;font-weight:500;line-height:1;min-width:2rem}
.lp-legend dt b{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.16em}
.lp-legend dd{margin:0;font-size:14px;color:var(--lp-dim)}
.lp-table{width:100%;border-collapse:collapse;margin-bottom:34px}
.lp-table tr{border-bottom:1px solid var(--line-dark)}
.lp-table tr:first-child{border-top:1px solid var(--line-dark)}
.lp-table th{text-align:left;padding:11px 20px 11px 0;width:11rem;vertical-align:baseline}
.lp-table td{padding:11px 0;font-size:14px;color:var(--lp-dim);vertical-align:baseline}
.lp-sub{font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:clamp(15px,1.5vw,19px);
  margin:0 0 14px}
.lp-callout{border:1px solid var(--line-dark);border-radius:16px;padding:clamp(22px,3vw,34px);margin-top:30px}
.lp-callout h3{margin:0 0 12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:17px}
.lp-callout p{margin:0;font-size:15px;line-height:1.7;color:var(--lp-dim)}
.lp-notice{border:1px solid var(--line-dark);border-radius:16px;padding:24px;margin:26px 0 0}
.lp-notice h3{margin:0 0 10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:15px}
.lp-notice p{margin:0;font-size:14px;line-height:1.7;color:var(--lp-dim)}

.lp-end{text-align:center;padding:clamp(60px,10vh,120px) var(--pad);border-top:1px solid var(--line-dark)}
.lp-end h2{font-size:clamp(30px,6vw,84px);letter-spacing:-.03em;line-height:.95;text-transform:uppercase}
.lp-end p{margin:22px auto 0;max-width:46ch;font-size:16px;line-height:1.6;color:var(--lp-dim)}

@media(max-width:820px){
  .lp-legend div{grid-template-columns:1fr;gap:.3rem}
  .lp-tips{grid-template-columns:1fr}
  .lp-nav{top:50px}
}
@media(prefers-reduced-motion:reduce){
  .lp-tip,.lp-tip::before{transition:none}
  .lp-tip:hover{transform:none}
}
"""


def tip(t, i):
    keys = t.get("k")
    cls = "lp-tip reveal" + ("" if keys else " no-keys") + (
        " is-key" if t.get("b") == HIGHLIGHT else "")
    out = [f'<article class="{cls}">', '<div class="lp-tip-head">',
           f'<span class="lp-num">{i:03d}</span>']
    if t.get("b"):
        out.append(f'<span class="lp-badge">{esc(t["b"])}</span>')
    out.append("</div>")
    out.append(f'<h4>{esc(t["t"])}</h4>')
    out.append(f'<p>{esc(t["d"])}</p>')
    if keys:
        k = keycap(keys).replace('class="kbd kbd-phrase"', 'class="lp-kbd phrase"')
        k = k.replace('class="kbd"', 'class="lp-kbd"')
        out.append(f'<div class="lp-keys">{k}</div>')
    out.append("</article>")
    return "".join(out)


def front_block(p):
    o = [f'<section class="lp-block lp-doc" id="{p["id"]}">',
         '<div class="lp-block-head reveal">',
         f'<p class="lp-eyebrow">{esc(p["kicker"])}</p>',
         f'<h2>{esc(p["title"])}</h2></div>']
    for para in p.get("body", []):
        o.append(f'<p class="lp-intro reveal">{esc(para)}</p>')
    if p.get("list"):
        o.append('<ul class="lp-rules reveal">')
        o += [f"<li>{esc(x)}</li>" for x in p["list"]]
        o.append("</ul>")
    if p.get("keys"):
        o.append('<dl class="lp-legend reveal">')
        for k in p["keys"]:
            o.append(f'<div><dt><span class="lp-sym">{esc(k["sym"])}</span>'
                     f'<b>{esc(k["name"])}</b></dt><dd>{esc(k["note"])}</dd></div>')
        o.append("</dl>")
    for tb in p.get("tables", []):
        o.append('<div class="reveal">')
        o.append(f'<h3 class="lp-sub">{esc(tb["heading"])}</h3><table class="lp-table"><tbody>')
        for key, d in tb["rows"]:
            o.append(f'<tr><th><span class="lp-kbd">{esc(key)}</span></th><td>{esc(d)}</td></tr>')
        o.append("</tbody></table></div>")
    if p.get("callout"):
        c = p["callout"]
        o.append(f'<aside class="lp-callout reveal"><h3>{esc(c["title"])}</h3>'
                 f'<p>{esc(c["text"])}</p></aside>')
    o.append("</section>")
    return "".join(o)


def section_block(s, start):
    total = sum(len(g["tips"]) for g in s["groups"])
    o = [f'<section class="lp-block" id="{slug(s)}">',
         '<div class="lp-block-head reveal">',
         f'<p class="lp-eyebrow">Section {s["number"]:02d}</p>',
         f'<h2>{esc(s["title"])}.</h2>',
         f'<p class="lp-count">{total} tricks</p></div>',
         f'<p class="lp-intro reveal">{esc(s["intro"])}</p>']
    if s.get("notice"):
        n = s["notice"]
        o.append(f'<aside class="lp-notice reveal"><h3>{esc(n["title"])}</h3>'
                 f'<p>{esc(n["text"])}</p></aside>')
    i = start
    for g in s["groups"]:
        o.append('<div class="lp-group">')
        o.append('<div class="lp-group-head reveal"><h3>' + esc(g["heading"]) + "</h3>")
        if g.get("path"):
            o.append(f'<p class="lp-path">{esc(g["path"])}</p>')
        o.append("</div>")
        if g.get("note"):
            o.append(f'<p class="lp-note reveal">{esc(g["note"])}</p>')
        o.append('<div class="lp-tips">')
        for n, t in enumerate(g["tips"]):
            # stagger the first three of every row the way the site does
            html = tip(t, i)
            if n % 3 in (1, 2):
                html = html.replace("lp-tip reveal", f"lp-tip reveal d{n % 3}", 1)
            o.append(html)
            i += 1
        o.append("</div></div>")
    o.append("</section>")
    return "".join(o), i


NAV_JS = """
<script>
/* Sticky section nav: drag-to-scroll, edge fades and an active highlight.
   Mirrors the behaviour of the site's other jump bars but is self-contained,
   so this page does not depend on markup that lives elsewhere. */
(function () {
  var bar = document.querySelector('.lp-nav-inner');
  if (!bar) return;
  var links = Array.prototype.slice.call(bar.querySelectorAll('a'));
  var blocks = links.map(function (a) {
    return document.getElementById(a.getAttribute('href').slice(1));
  }).filter(Boolean);

  var down = false, dragging = false, moved = false, startX = 0, startLeft = 0;
  bar.addEventListener('pointerdown', function (e) {
    if (e.button && e.button !== 0) return;
    down = true; dragging = false; moved = false;
    startX = e.clientX; startLeft = bar.scrollLeft;
  });
  bar.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - startX;
    if (!dragging && Math.abs(dx) > 4) { dragging = true; moved = true; bar.classList.add('dragging'); }
    if (dragging) bar.scrollLeft = startLeft - dx;
  });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (ev) {
    bar.addEventListener(ev, function () { down = dragging = false; bar.classList.remove('dragging'); });
  });
  bar.addEventListener('click', function (e) {
    if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
  }, true);

  var current = null;
  function setActive(el) {
    if (el === current) return;
    current = el;
    links.forEach(function (a) { a.classList.remove('active'); });
    if (!el) return;
    el.classList.add('active');
    if (down) return;
    var r = el.getBoundingClientRect(), b = bar.getBoundingClientRect();
    if (r.left < b.left + 8 || r.right > b.right - 8) {
      bar.scrollTo({ left: bar.scrollLeft + (r.left - b.left) - (b.width / 2 - r.width / 2),
                     behavior: 'smooth' });
    }
  }
  var ticking = false;
  function spy() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var best = null;
      for (var i = 0; i < blocks.length; i++) {
        if (blocks[i].getBoundingClientRect().top - 170 <= 0) best = links[i];
        else break;
      }
      setActive(best);
    });
  }
  window.addEventListener('scroll', spy, { passive: true });
  spy();
})();
</script>
"""


def main():
    front, sections = load()
    total = count_tips(sections)

    nav = ['<nav class="lp-nav" aria-label="Sections"><div class="lp-nav-inner">']
    for p in front["pages"]:
        nav.append(f'<a href="#{p["id"]}">{esc(p["label"])}</a>')
    for s in sections:
        nav.append(f'<a href="#{slug(s)}"><i>{s["number"]:02d}</i>{esc(s["title"])}</a>')
    nav.append("</div></nav>")

    body = [head(), '<section class="proj lp">',
            '<div class="lp-hero">',
            '<p class="lp-eyebrow reveal">Free resource &middot; Logic Pro</p>',
            '<h1 class="reveal d1">Logic Pro<br>Crash Course</h1>',
            f'<p class="lp-lead reveal d1">{total} tricks I actually use, across '
            f'{len(sections)} sections — key commands, editing, mixing, and the settings '
            'worth changing before you record a note. Built to be searched mid-session, '
            'not read cover to cover.</p>',
            '<div class="lp-stats reveal d2">',
            f'<div class="lp-stat"><b>{total}</b><span>Tricks</span></div>',
            f'<div class="lp-stat"><b>{len(sections)}</b><span>Sections</span></div>',
            '<div class="lp-stat"><b>Free</b><span>To keep</span></div></div>',
            f'<div class="lp-cta reveal d3"><a class="pill" href="{PDF_HREF}" download>'
            'Download the PDF</a></div>',
            "</div>"]
    body += nav
    body.append('<div class="lp-body">')
    for p in front["pages"]:
        body.append(front_block(p))
    i = 1
    for s in sections:
        chunk, i = section_block(s, i)
        body.append(chunk)
    body.append("</div>")

    body.append('<div class="lp-end">'
                f'<h2 class="reveal">That&rsquo;s the {total}.</h2>'
                '<p class="reveal d1">Take what is useful and go and finish the song. '
                'Come back whenever you get stuck — every section is one tap away.</p>'
                f'<div class="lp-cta reveal d2"><a class="pill" href="{PDF_HREF}" download>'
                'Download the PDF</a></div></div>')
    body.append("</section>")

    body.append(FOOTER)
    body.append(NAV_JS)
    body.append("</body>\n</html>\n")

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course-page.html"
    out.write_text("".join(body), encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"Tricks: {total}   Sections: {len(sections)}")
    print(f"Drop at the site root; PDF expected at {PDF_HREF}")


FOOTER = """
<footer class="foot">
  <div class="ready reveal"><a href="contact.html">Ready to work together?</a></div>
  <div class="foot-cols">
    <div class="fcol reveal">
      <h4>Explore</h4>
      <a href="work.html">Work</a>
      <a href="maccaroni.html">Maccaroni</a>
      <a href="services.html">Work with me</a><a href="contact.html">Contact</a>
    </div>
    <div class="fcol reveal d1">
      <h4>Connect<br>With Me</h4>
      <a href="https://www.instagram.com/dannnymaccc_/" target="_blank" rel="noopener">Instagram</a><a href="https://www.youtube.com/channel/UCwNgSiOTmtKOH5ybC1zxwrw" target="_blank" rel="noopener">YouTube</a><a href="https://www.linkedin.com/in/danielmccarthy23" target="_blank" rel="noopener">LinkedIn</a>
    </div>
    <div class="fcol newsletter reveal d2">
      <h4>Let's Be<br>Friends</h4>
      <p class="copy">Drop your email address to receive news and updates.</p>
      <form name="newsletter" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="?signup=1">
        <input type="hidden" name="form-name" value="newsletter">
        <p class="hidden"><label>Skip<input name="bot-field"></label></p>
        <input type="email" name="email" placeholder="Email Address" required>
        <button type="submit">Sign Up</button>
      </form>
    </div>
  </div>
  <div class="base">
    <span>&copy; 2026 Dannny McCcarthy</span>
    <span>Brand Identity &amp; Strategy in Seattle</span>
  </div>
</footer>
"""


if __name__ == "__main__":
    main()
