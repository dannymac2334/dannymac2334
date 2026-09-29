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

import json
import pathlib

from build import (esc, keycap, load, slug, count_tips, sources_html, numbered_refs, legal_notice,
                   load_extras, term_pattern, link_terms)

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# The PDF is paid content: it is never a public file. The site agent wires
# /download to a function that checks the buyer's key and returns a signed URL.
PDF_HREF = "/download"
HIGHLIGHT = "GAME CHANGER"

TITLE = "Logic Pro Crash Course | Dannny McCcarthy"
_front, _sections = load()
TRICKS = count_tips(_sections)
DESC = (f"{TRICKS} Logic Pro tricks across {len(_sections)} sections — key commands, editing, mixing and "
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
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"Logic Pro Crash Course","description":"{DESC}","inLanguage":"en","image":"https://www.dannnymcccarthy.com/assets/brand/og-cover.jpg","mainEntityOfPage":{{"@type":"WebPage","@id":"{URL}"}},"author":{{"@type":"Person","name":"Daniel McCarthy","alternateName":"Dannny McCcarthy","url":"https://www.dannnymcccarthy.com"}},"publisher":{{"@type":"ProfessionalService","name":"Dannny McCcarthy","url":"https://www.dannnymcccarthy.com"}},"about":{{"@type":"SoftwareApplication","name":"Logic Pro","applicationCategory":"MultimediaApplication","operatingSystem":"macOS"}},"keywords":"Logic Pro, music production, key commands, mixing, MIDI, recording, workflow"}}
</script>
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

/* filter bar — hundreds of tricks on one page is a search problem, not a scroll problem */
.lp-tools{position:sticky;top:56px;z-index:91;padding:12px var(--pad);box-sizing:border-box;
  background:rgba(0,0,0,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
  border-top:1px solid var(--line-dark)}
.lp-tools-inner{max-width:1200px;margin:0 auto;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.lp-search{position:relative;flex:1 1 280px;min-width:0}
.lp-search input{width:100%;background:transparent;border:1px solid #3a3a3a;border-radius:100px;
  color:#fff;font-family:inherit;font-size:13px;letter-spacing:.02em;padding:11px 74px 11px 18px;
  outline:none;transition:border-color .25s var(--ease)}
.lp-search input::placeholder{color:#7d7d7a}
.lp-search input:focus{border-color:#fff}
.lp-search kbd{position:absolute;right:14px;top:50%;transform:translateY(-50%);pointer-events:none;
  font-family:inherit;font-size:9px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:#7d7d7a;border:1px solid #3a3a3a;border-radius:100px;padding:3px 8px}
.lp-search input:not(:placeholder-shown)+kbd{display:none}
.lp-toggle{flex:0 0 auto;cursor:pointer;background:transparent;color:#e8e8e6;border:1px solid #3a3a3a;
  border-radius:100px;font-family:inherit;font-weight:500;font-size:11px;text-transform:uppercase;
  letter-spacing:.12em;padding:10px 18px;white-space:nowrap;
  transition:background .25s var(--ease),border-color .25s var(--ease),color .25s var(--ease)}
.lp-toggle:hover{background:#141414;border-color:#5a5a5a;color:#fff}
.lp-toggle[aria-pressed="true"]{background:#fff;border-color:#fff;color:#000}
.lp-count-live{flex:0 0 auto;font-size:10px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;
  color:#8a8a86;font-variant-numeric:tabular-nums}
.lp-empty{display:none;text-align:center;padding:clamp(60px,12vh,140px) var(--pad)}
.lp-empty h3{font-size:clamp(22px,3.4vw,40px);letter-spacing:-.02em;text-transform:uppercase;margin:0}
.lp-empty p{margin:16px auto 0;max-width:40ch;color:var(--lp-dim);font-size:15px}
.lp.is-empty .lp-empty{display:block}
.lp.is-filtering .lp-doc{display:none}
.lp.is-filtering .lp-nav-inner a.dim{opacity:.3}

/* back to top — the page is long enough to earn one */
.lp-top{position:fixed;right:22px;bottom:22px;z-index:95;opacity:0;pointer-events:none;
  transform:translateY(8px);transition:opacity .3s var(--ease),transform .3s var(--ease);
  background:#fff;color:#000;border:0;border-radius:100px;cursor:pointer;font-family:inherit;
  font-weight:600;font-size:10px;letter-spacing:.16em;text-transform:uppercase;padding:13px 20px}
.lp-top.show{opacity:1;pointer-events:auto;transform:none}

.lp :focus-visible,.lp-tools :focus-visible,.lp-nav :focus-visible{outline:2px solid #fff;outline-offset:3px}
.visually-hidden{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;
  clip:rect(0 0 0 0);white-space:nowrap;border:0}
/* Once filtering starts, stop hiding things behind the scroll reveal — a match
   that has never been scrolled past would otherwise come back as an empty slot.
   The transition is killed too, so results appear instantly instead of fading
   in over .9s, which would read as lag while typing. */
.lp.no-anim .reveal{opacity:1 !important;transform:none !important;transition:none !important}

/* sticky section nav — same behaviour language as the site's other jump bars */
.lp-nav{position:sticky;top:110px;z-index:90;padding:11px var(--pad);box-sizing:border-box;
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
.lp-src{margin:0;padding:12px 22px 18px;border-radius:0 0 15px 15px;font-size:11px;line-height:1.5;
  color:var(--lp-dim);flex:0 0 auto}
.lp-src span{font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:9px;opacity:.7;margin-right:4px}
.lp-src a{color:inherit;text-decoration:underline;text-decoration-color:rgba(255,255,255,.3);text-underline-offset:2px}
.lp-src a:hover{text-decoration-color:currentColor}
.lp-src-intro,.lp-notice .lp-src{padding:6px 0 0;background:none}
/* beginner layer — ask in your own words, pick a goal, tap a word you don't know */
.lp-ask{flex:1 0 100%;margin:0 0 2px;font-size:clamp(20px,2.4vw,30px);font-weight:700;letter-spacing:-.02em;
  text-transform:uppercase;line-height:1.05}
.lp-chips{flex:1 0 100%;display:flex;gap:8px;overflow-x:auto;padding:2px 0 4px;scrollbar-width:none;
  -webkit-overflow-scrolling:touch}
.lp-chips::-webkit-scrollbar{display:none}
.lp-chip{flex:0 0 auto;cursor:pointer;background:transparent;color:#d5d4cf;border:1px solid #3a3a3a;
  border-radius:100px;font-family:inherit;font-size:12px;padding:8px 14px;white-space:nowrap;
  transition:background .25s var(--ease),border-color .25s var(--ease),color .25s var(--ease)}
.lp-chip:hover{border-color:#5a5a5a;color:#fff}
.lp-chip[aria-pressed="true"]{background:#fff;border-color:#fff;color:#000}
.lp-badge.lp-start{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.55)}
.lp-gl{position:relative;cursor:help;text-decoration:underline dotted;text-underline-offset:3px;
  text-decoration-color:rgba(255,255,255,.5);outline:none}
.lp-gl:hover::after,.lp-gl:focus::after{content:attr(data-def);position:absolute;left:0;bottom:calc(100% + 8px);
  z-index:30;width:min(280px,70vw);background:#fff;color:#000;font-size:12.5px;line-height:1.5;
  font-weight:400;letter-spacing:0;text-transform:none;padding:10px 12px;border-radius:10px;
  box-shadow:0 12px 30px -12px rgba(0,0,0,.6);white-space:normal}
.lp-defs{max-width:1200px;margin:0 auto;padding:0 var(--pad)}
.lp-def{margin:22px 0 0;border:1px solid var(--line-dark);border-radius:16px;padding:18px 22px}
.lp-def span{display:block;font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;opacity:.6}
.lp-def b{display:block;margin-top:6px;font-size:20px;letter-spacing:-.01em}
.lp-def p{margin:6px 0 0;color:var(--lp-dim);font-size:14px;line-height:1.6;max-width:70ch}
.lp-def a{display:inline-block;margin-top:8px;font-size:12px;color:#fff}
.lp-steps{list-style:none;margin:26px 0 0;padding:0;display:grid;gap:4px;max-width:880px}
.lp-steps li{display:grid;grid-template-columns:48px 1fr;gap:16px;border-top:1px solid var(--line-dark);padding:18px 0}
.lp-step-n{font-size:28px;font-weight:700;letter-spacing:-.03em;line-height:1}
.lp-steps h3{margin:0;font-size:17px;font-weight:600;text-transform:none;letter-spacing:0}
.lp-steps p{margin:6px 0 0;color:var(--lp-dim);font-size:14.5px;line-height:1.65}
.lp-steps .lp-keys{padding:10px 0 0;background:none}
.lp-goal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin-top:24px}
.lp-goal-btn{display:flex;justify-content:space-between;align-items:center;gap:12px;cursor:pointer;text-align:left;
  background:transparent;color:#fff;border:1px solid var(--line-dark);border-radius:14px;font-family:inherit;
  font-size:14px;padding:16px 18px;transition:border-color .25s var(--ease),background .25s var(--ease)}
.lp-goal-btn:hover{border-color:#fff;background:#0d0d0d}
.lp-goal-btn span{font-size:11px;letter-spacing:.1em;opacity:.6}
.lp-gloss{margin:24px 0 0;columns:2 320px;column-gap:40px}
.lp-gloss>div{break-inside:avoid;border-top:1px solid var(--line-dark);padding:14px 0}
.lp-gloss dt{font-weight:600;font-size:15px}
.lp-gloss dt small{display:block;font-weight:400;font-size:11px;opacity:.6;margin-top:2px}
.lp-gloss dd{margin:6px 0 0;color:var(--lp-dim);font-size:13.5px;line-height:1.6}
.lp-legal{max-width:1100px;margin:40px auto 0;padding:0 clamp(16px,4vw,40px);font-size:11px;line-height:1.6;color:var(--lp-dim);opacity:.75}
sup.ref{font-size:10px;font-weight:600;margin-left:3px;color:var(--lp-dim)}
.ref-n{font-weight:600;font-size:10px;opacity:.8}
.lp-tip:has(.lp-src) .lp-keys{padding-bottom:0;border-radius:0}
.lp-tip.no-keys:has(.lp-src) p{padding-bottom:0;border-radius:0}
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


EXTRA = {"rx": None, "lookup": {}, "defs": {}, "goals": {}}


def gl_span(txt, gid):
    """Jargon inside a trick: tap or hover for the plain-English meaning."""
    d = EXTRA["defs"].get(gid, "")
    return (f'<span class="lp-gl" tabindex="0" data-def="{esc(d).replace(chr(34), "&quot;")}">'
            f'{txt}</span>')


def tip(t, i):
    keys = t.get("k")
    cls = "lp-tip reveal" + ("" if keys else " no-keys") + (
        " is-key" if t.get("b") == HIGHLIGHT else "")
    goals = t.get("goals", [])
    words = " ".join(w for g in goals for w in [EXTRA["goals"].get(g, {}).get("label", ""),
                                                  *EXTRA["goals"].get(g, {}).get("synonyms", [])])
    out = [f'<article class="{cls}" id="t-{i}" data-goals="{" ".join(goals)}" '
           f'data-lvl="{t.get("lvl", 2)}" data-k="{esc(words)}">', '<div class="lp-tip-head">',
           f'<span class="lp-num">{i:03d}</span>']
    if t.get("lvl") == 1:
        out.append('<span class="lp-badge lp-start">Start here</span>')
    if t.get("b"):
        out.append(f'<span class="lp-badge">{esc(t["b"])}</span>')
    out.append("</div>")
    out.append(f'<h4>{esc(t["t"])}</h4>')
    out.append(f'<p>{link_terms(esc(t["d"]), EXTRA["rx"], EXTRA["lookup"], gl_span)}</p>')
    if keys:
        k = keycap(keys).replace('class="kbd kbd-phrase"', 'class="lp-kbd phrase"')
        k = k.replace('class="kbd"', 'class="lp-kbd"')
        out.append(f'<div class="lp-keys">{k}</div>')
    if t.get("src"):
        out.append(sources_html(t["src"], cls="lp-src"))
    out.append("</article>")
    return "".join(out)


def front_block(p):
    o = [f'<section class="lp-block lp-doc" id="{p["id"]}">',
         '<div class="lp-block-head reveal">',
         f'<p class="lp-eyebrow">{esc(p["kicker"])}</p>',
         f'<h2>{esc(p["title"])}</h2></div>']
    for para in p.get("body", []):
        o.append(f'<p class="lp-intro reveal">{esc(para)}</p>')
    if p.get("steps"):
        o.append('<ol class="lp-steps">')
        for n, st in enumerate(p["steps"], 1):
            k = ""
            if st.get("key"):
                cap = keycap(st["key"]).replace('class="kbd"', 'class="lp-kbd"')
                k = f'<div class="lp-keys">{cap}</div>'
            o.append(f'<li class="reveal"><span class="lp-step-n">{n}</span><div><h3>{esc(st["title"])}</h3>'
                     f'<p>{link_terms(esc(st["body"]), EXTRA["rx"], EXTRA["lookup"], gl_span)}</p>{k}'
                     + (sources_html(st["src"], cls="lp-src lp-src-intro") if st.get("src") else "")
                     + "</div></li>")
        o.append("</ol>")
    if p.get("generated") == "goals":
        o.append('<div class="lp-goal-grid reveal">' + "".join(
            f'<button class="lp-goal-btn" type="button" data-goal="{g["id"]}">{esc(g["label"])}'
            f'<span>{EXTRA["goal_counts"].get(g["id"], 0)}</span></button>'
            for g in EXTRA["goal_list"] if EXTRA["goal_counts"].get(g["id"])) + "</div>")
    if p.get("generated") == "glossary":
        o.append('<dl class="lp-gloss">' + "".join(
            f'<div id="g-{e["id"]}"><dt>{esc(e["term"])}'
            + (f'<small>also: {esc(", ".join(e["aka"]))}</small>' if e.get("aka") else "")
            + f'</dt><dd>{esc(e["def"])}'
            + (sources_html(e["src"], cls="lp-src lp-src-intro") if e.get("src") else "") + "</dd></div>"
            for e in sorted(EXTRA["glossary"], key=lambda e: e["term"].lower())) + "</dl>")
    if p.get("list"):
        o.append('<ul class="lp-rules reveal">')
        o += [f"<li>{esc(x)}</li>" for x in p["list"]]
        o.append("</ul>")
    if p.get("keys"):
        marks, refs = numbered_refs([k.get("src") for k in p["keys"]])
        o.append('<dl class="lp-legend reveal">')
        for k, mark in zip(p["keys"], marks):
            o.append(f'<div><dt><span class="lp-sym">{esc(k["sym"])}</span>'
                     f'<b>{esc(k["name"])}</b></dt><dd>{esc(k["note"])}{mark}</dd></div>')
        o.append("</dl>")
        o.append(refs.replace('class="doc-src"', 'class="lp-src lp-src-intro"'))
    for tb in p.get("tables", []):
        o.append('<div class="reveal">')
        o.append(f'<h3 class="lp-sub">{esc(tb["heading"])}</h3><table class="lp-table"><tbody>')
        marks, refs = numbered_refs([row[2] if len(row) > 2 else None for row in tb["rows"]])
        for (key, d, *_), mark in zip(tb["rows"], marks):
            o.append(f'<tr><th><span class="lp-kbd">{esc(key)}</span></th><td>{esc(d)}{mark}</td></tr>')
        o.append("</tbody></table>")
        o.append(refs.replace('class="doc-src"', 'class="lp-src lp-src-intro"'))
        o.append("</div>")
    if p.get("callout"):
        c = p["callout"]
        o.append(f'<aside class="lp-callout reveal"><h3>{esc(c["title"])}</h3>'
                 f'<p>{esc(c["text"])}</p>'
                 + (sources_html(c["src"], cls="lp-src lp-src-intro") if c.get("src") else "")
                 + '</aside>')
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
    if s.get("intro_src"):
        o.append(sources_html(s["intro_src"], cls="lp-src lp-src-intro reveal"))
    if s.get("notice"):
        n = s["notice"]
        o.append(f'<aside class="lp-notice reveal"><h3>{esc(n["title"])}</h3>'
                 f'<p>{esc(n["text"])}</p>'
                 + (sources_html(n["src"], cls="lp-src") if n.get("src") else "")
                 + '</aside>')
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
    links.forEach(function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
    if (!el) return;
    el.classList.add('active');
    el.setAttribute('aria-current', 'true');
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

  /* ---- search: by what you want to do ------------------------------
     Beginners search in their own words ("make drums louder"), not Logic's.
     Each card carries its goals and their everyday synonyms (data-k), filler
     words are dropped, and plurals / -ing forms still match. Goal chips and the
     Start here toggle narrow further. A matching glossary term is explained
     above the results. */
  var page = document.querySelector('.lp');
  var input = document.getElementById('lp-q');
  var gcBtn = document.getElementById('lp-gc');
  var stBtn = document.getElementById('lp-start');
  var countEl = document.getElementById('lp-count');
  var emptyEl = document.querySelector('.lp-empty');
  var defsEl = document.querySelector('.lp-defs');
  if (!input || !page) return;
  var gloss = [];
  try { gloss = JSON.parse((document.getElementById('lp-gloss') || {}).textContent || '[]'); } catch (e) {}

  var STOP = ' a an the to i im want wanna how do does can my me in on of for with and or is it what make '
           + 'get my some this that you your use using logic pro ';
  function words(q) {
    return q.toLowerCase().replace(/[^\\w\\s#⌘⌥⇧⌃-]/g, ' ').split(/\\s+/).filter(function (w) {
      return w && STOP.indexOf(' ' + w + ' ') === -1;
    });
  }
  function stems(w) {
    var out = [w];
    var base = w.replace(/(ing|ers|er|ed|es|s)$/, '');
    if (base.length >= 3 && base !== w) out.push(base);
    return out;
  }

  var cards = Array.prototype.slice.call(page.querySelectorAll('.lp-tip'));
  var total = cards.length;
  cards.forEach(function (c) {
    var block = c.closest('.lp-block');
    var group = c.closest('.lp-group');
    var src = c.querySelector('.lp-src');
    c._t = [
      src ? c.textContent.replace(src.textContent, '') : c.textContent,
      c.getAttribute('data-k') || '',
      group ? group.querySelector('h3').textContent : '',
      block ? block.querySelector('h2').textContent : ''
    ].join(' ').toLowerCase().replace(/\\s+/g, ' ');
    c._g = ' ' + (c.getAttribute('data-goals') || '') + ' ';
  });
  var groups = Array.prototype.slice.call(page.querySelectorAll('.lp-group'));
  var sections = Array.prototype.slice.call(page.querySelectorAll('.lp-block:not(.lp-doc)'));
  var docs = Array.prototype.slice.call(page.querySelectorAll('.lp-doc'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-goal]'));
  var goal = '';

  function showDefs(ws) {
    if (!defsEl) return;
    if (!ws.length) { defsEl.innerHTML = ''; return; }
    var hits = gloss.filter(function (e) {
      var names = [e.t].concat(e.a || []).map(function (n) { return n.toLowerCase(); });
      var q = ws.join(' ');
      return names.some(function (n) { return n === q || ws.indexOf(n) !== -1; });
    }).slice(0, 3);
    defsEl.innerHTML = hits.map(function (e) {
      var d = document.createElement('div'); d.textContent = e.d;
      var t = document.createElement('b'); t.textContent = e.t;
      return '<div class="lp-def"><span>What is it?</span>' + t.outerHTML + '<p>' + d.innerHTML +
             '</p><a href="#g-' + e.id + '">In the glossary</a></div>';
    }).join('');
  }

  function apply() {
    var ws = words(input.value);
    var gcOnly = gcBtn.getAttribute('aria-pressed') === 'true';
    var stOnly = stBtn && stBtn.getAttribute('aria-pressed') === 'true';
    var filtering = !!ws.length || gcOnly || stOnly || !!goal;
    page.classList.toggle('is-filtering', filtering);
    if (filtering) page.classList.add('no-anim');
    showDefs(ws);

    var shown = 0;
    cards.forEach(function (c) {
      var ok = ws.every(function (w) {
        return stems(w).some(function (v) { return c._t.indexOf(v) !== -1; });
      });
      ok = ok && (!gcOnly || c.classList.contains('is-key'))
              && (!stOnly || c.getAttribute('data-lvl') === '1')
              && (!goal || c._g.indexOf(' ' + goal + ' ') !== -1);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      g.style.display = g.querySelector('.lp-tip:not([style*="none"])') ? '' : 'none';
    });
    sections.forEach(function (s) {
      var any = s.querySelector('.lp-tip:not([style*="none"])');
      s.style.display = any ? '' : 'none';
      var link = bar.querySelector('a[href="#' + s.id + '"]');
      if (link) link.classList.toggle('dim', !any);
    });
    docs.forEach(function (d) { d.style.display = filtering ? 'none' : ''; });
    chips.forEach(function (ch) { ch.setAttribute('aria-pressed', ch.getAttribute('data-goal') === goal ? 'true' : 'false'); });

    page.classList.toggle('is-empty', filtering && shown === 0);
    countEl.textContent = filtering ? shown + ' of ' + total + ' tricks' : total + ' tricks';
    if (emptyEl) emptyEl.hidden = !(filtering && shown === 0);
  }

  var t;
  input.addEventListener('input', function () {
    clearTimeout(t);
    t = setTimeout(apply, 90);
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { input.value = ''; goal = ''; apply(); input.blur(); }
  });
  [gcBtn, stBtn].forEach(function (btn) {
    if (!btn) return;
    btn.addEventListener('click', function () {
      btn.setAttribute('aria-pressed', btn.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      apply();
    });
  });
  chips.forEach(function (ch) {
    ch.addEventListener('click', function () {
      var g = ch.getAttribute('data-goal');
      goal = goal === g ? '' : g;
      apply();
      var tools = document.querySelector('.lp-tools');
      if (tools) window.scrollTo({ top: tools.getBoundingClientRect().top + window.scrollY - 60, behavior: 'smooth' });
    });
  });
  // "/" focuses search — fitting for a book about key commands
  document.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return;
    var el = document.activeElement, tag = el && el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (el && el.isContentEditable)) return;
    e.preventDefault();
    input.focus();
    input.select();
  });

  /* ---- back to top ---- */
  var top = document.querySelector('.lp-top');
  if (top) {
    top.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      input.blur();
    });
    var tick = false;
    window.addEventListener('scroll', function () {
      if (tick) return;
      tick = true;
      requestAnimationFrame(function () {
        tick = false;
        top.classList.toggle('show', window.scrollY > 1400);
      });
    }, { passive: true });
  }
})();
</script>
"""


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
    n_src = sum(len(t.get("src", [])) for sec in sections for g in sec["groups"] for t in g["tips"])

    chips = "".join(
        f'<button class="lp-chip" type="button" data-goal="{g["id"]}">{esc(g["label"])}</button>'
        for g in goal_list if counts.get(g["id"]))
    tools = [
        '<div class="lp-tools">',
        '<div class="lp-tools-inner">',
        '<p class="lp-ask">What do you want to do?</p>',
        '<div class="lp-search" role="search">',
        '<label class="visually-hidden" for="lp-q">Search the tricks</label>',
        '<input id="lp-q" type="search" autocomplete="off" spellcheck="false" '
        'placeholder="Try: make a beat, record vocals, fix timing, louder…">',
        "<kbd>/</kbd>",
        "</div>",
        '<button class="lp-toggle" type="button" id="lp-start" aria-pressed="false">Start here</button>',
        '<button class="lp-toggle" type="button" id="lp-gc" aria-pressed="false">Game changers</button>',
        f'<p class="lp-count-live" id="lp-count" aria-live="polite">{total} tricks</p>',
        f'<div class="lp-chips" role="group" aria-label="Goals">{chips}</div>',
        "</div></div>",
    ]

    nav = ['<nav class="lp-nav" aria-label="Sections"><div class="lp-nav-inner">']
    for p in front["pages"]:
        if not p.get("back"):
            nav.append(f'<a href="#{p["id"]}">{esc(p["label"])}</a>')
    for s in sections:
        nav.append(f'<a href="#{slug(s)}"><i>{s["number"]:02d}</i>{esc(s["title"])}</a>')
    for p in front["pages"]:
        if p.get("back"):
            nav.append(f'<a href="#{p["id"]}">{esc(p["label"])}</a>')
    nav.append("</div></nav>")

    body = [head(), '<section class="proj lp">',
            '<div class="lp-hero">',
            '<p class="lp-eyebrow reveal">Your library &middot; Logic Pro 11 &amp; 12</p>',
            '<h1 class="reveal d1">Logic Pro<br>Crash Course</h1>',
            f'<p class="lp-lead reveal d1">{total} tricks for Logic Pro, each checked against the source '
            'it cites. Search for what you want to do, or tap a goal. Never opened Logic before? Tap '
            '<a href="#start">Start here</a> first.</p>',
            '<div class="lp-stats reveal d2">',
            f'<div class="lp-stat"><b>{total}</b><span>Tricks</span></div>',
            f'<div class="lp-stat"><b>{len(sections)}</b><span>Sections</span></div>',
            f'<div class="lp-stat"><b>{n_src}</b><span>Sources</span></div></div>',
            f'<div class="lp-cta reveal d3"><a class="pill" href="{PDF_HREF}">'
            'Download the PDF</a></div>',
            "</div>"]
    body += tools
    body += nav
    body.append('<div class="lp-defs" aria-live="polite"></div>')
    body.append('<div class="lp-empty"><h3>Nothing matches that yet.</h3>'
                '<p>Try a simpler word — drums, vocals, loop, louder — or tap one of the goals above.</p></div>')
    body.append('<div class="lp-body">')
    for p in front["pages"]:
        if not p.get("back"):
            body.append(front_block(p))
    i = 1
    for s in sections:
        chunk, i = section_block(s, i)
        body.append(chunk)
    for p in front["pages"]:
        if p.get("back"):
            body.append(front_block(p))
    body.append("</div>")

    body.append('<div class="lp-end">'
                f'<h2 class="reveal">That&rsquo;s the {total}.</h2>'
                '<p class="reveal d1">Take what is useful and go and finish the song. '
                'Come back whenever you get stuck — every section is one tap away.</p>'
                f'<div class="lp-cta reveal d2"><a class="pill" href="{PDF_HREF}">'
                'Download the PDF</a></div></div>')
    body.append("</section>")

    body.append('<button class="lp-top" type="button">Back to top</button>')
    body.append(f'<p class="lp-legal">{esc(legal_notice())}</p>')
    gl = [{"t": e["term"], "a": e.get("aka", []), "d": e["def"], "id": e["id"]} for e in glossary]
    body.append('<script type="application/json" id="lp-gloss">'
                + json.dumps(gl, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    body.append(FOOTER)
    body.append(NAV_JS)
    body.append("</body>\n</html>\n")

    DIST.mkdir(exist_ok=True)
    out = DIST / "logic-pro-crash-course-page.html"
    out.write_text("".join(body), encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"Tricks: {total}   Sections: {len(sections)}   Glossary: {len(glossary)}   Goals: {len(counts)}")


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
