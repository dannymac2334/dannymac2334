#!/usr/bin/env python3
"""UX review of the built pages: no grey text, nothing touching.

For every page at desktop and phone width (and the book in print layout):
  grey     any visible text whose rendered colour is not pure black/ink or white,
           or that is faded with opacity
  touch    two visible "objects" (cards, pills, key caps, badges, buttons, inputs,
           text blocks) in the same container that overlap or sit closer than 4px

  python3 ux_check.py            # exit 1 if anything is found
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

DIST = pathlib.Path(__file__).parent / "dist"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PAGES = ["logic-pro-crash-course-page.html", "logic-pro-crash-course-sales.html", "logic-pro-crash-course.html"]
SIZES = [(1280, 900), (390, 844)]

JS = r"""
(opts) => {
  const OK = new Set(['rgb(0, 0, 0)', 'rgb(10, 10, 10)', 'rgb(255, 255, 255)']);
  const out = {grey: [], touch: []};
  const alpha = el => { let a = 1; for (let e = el; e; e = e.parentElement) a *= +getComputedStyle(e).opacity; return a; };
  const vis = el => {
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.display === 'none' || s.visibility === 'hidden' || e.hidden) return false;
    }
    return alpha(el) > 0.01;
  };
  const name = el => (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : el.tagName.toLowerCase())
                     + ' "' + (el.textContent || '').trim().slice(0, 34).replace(/\s+/g, ' ') + '"';
  // what is actually on screen: not hidden, not clipped away inside a scrolling panel
  const clipped = el => {
    const r = el.getBoundingClientRect();
    for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (/(auto|scroll|hidden)/.test(s.overflowY + s.overflowX)) {
        const c = e.getBoundingClientRect();
        if (r.top < c.top - 1 || r.bottom > c.bottom + 1 || r.left < c.left - 1 || r.right > c.right + 1) return true;
      }
    }
    return false;
  };
  const all = Array.from(document.querySelectorAll('body *')).filter(el => !['SCRIPT', 'STYLE', 'BR'].includes(el.tagName)
      && !el.classList.contains('visually-hidden') && vis(el) && !clipped(el));

  // 1. grey or faded text
  const seen = new Set();
  all.forEach(el => {
    const own = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const c = getComputedStyle(el).color, a = alpha(el);
    if (!OK.has(c) || a < 0.99) {
      const k = el.className + '|' + c;
      if (!seen.has(k)) { seen.add(k); out.grey.push(name(el) + '  color=' + c + (a < .99 ? ' opacity=' + a.toFixed(2) : '')); }
    }
  });

  // 2. what you can SEE of each element: its text lines, its card outline, or its divider lines
  const shapes = [];
  const range = document.createRange();
  all.forEach(el => {
    const s = getComputedStyle(el);
    if (s.position === 'fixed') return;
    const r = el.getBoundingClientRect();
    const bw = ['Top', 'Right', 'Bottom', 'Left'].map(k => parseFloat(s['border' + k + 'Width']) && s['border' + k + 'Style'] !== 'none' ? 1 : 0);
    const bg = s.backgroundColor !== 'rgba(0, 0, 0, 0)' && !/^(HTML|BODY|SECTION|MAIN)$/.test(el.tagName) && r.width < innerWidth * 0.9;
    if ((bw.every(Boolean) || bg) && r.width < innerWidth * 0.95) shapes.push({el, kind: 'box', r});
    else {
      if (bw[0]) shapes.push({el, kind: 'line', r: {left: r.left, right: r.right, top: r.top, bottom: r.top + 1}});
      if (bw[2]) shapes.push({el, kind: 'line', r: {left: r.left, right: r.right, top: r.bottom - 1, bottom: r.bottom}});
    }
    Array.from(el.childNodes).forEach(n => {
      if (n.nodeType !== 3 || !n.textContent.trim()) return;
      range.selectNodeContents(n);
      Array.from(range.getClientRects()).forEach(q => { if (q.width > 1) shapes.push({el, kind: 'text', r: q}); });
    });
    if (/^(IMG|SVG|svg)$/.test(el.tagName)) shapes.push({el, kind: 'text', r});
  });
  const inside = (a, b) => a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el);
  const gap = (a, b) => {
    const dx = Math.max(a.left - b.right, b.left - a.right, 0), dy = Math.max(a.top - b.bottom, b.top - a.bottom, 0);
    const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (ox > 0 && oy > 0) return -Math.min(ox, oy);
    return Math.max(dx, dy);
  };
  const tseen = new Set();
  // bucket by rows to keep this fast
  const B = 60, grid = new Map();
  shapes.forEach((s, i) => { for (let y = Math.floor(s.r.top / B); y <= Math.floor(s.r.bottom / B); y++) { if (!grid.has(y)) grid.set(y, []); grid.get(y).push(i); } });
  const done = new Set();
  grid.forEach(ids => {
    for (let x = 0; x < ids.length; x++) for (let y = x + 1; y < ids.length; y++) {
      const i = ids[x], j = ids[y], key = i < j ? i + ',' + j : j + ',' + i;
      if (done.has(key)) continue; done.add(key);
      const a = shapes[i], b = shapes[j];
      if (a.kind === 'line' && b.kind === 'line') continue;            // rules meeting rules is a table
      // overlays placed on purpose (the search icon inside the search box)
      if (getComputedStyle(a.el).position === 'absolute' || getComputedStyle(b.el).position === 'absolute') continue;
      // full-width bands stacked edge to edge (black section, paper section)
      const full = s => s.kind === 'box' && s.el.parentElement && s.r.width >= s.el.parentElement.getBoundingClientRect().width - 1;
      if (full(a) && full(b)) continue;
      if (a.kind === 'text' && b.kind === 'text' && a.el === b.el) continue;
      let g;
      const aHasB = a.el === b.el ? a.kind !== 'text' : a.el.contains(b.el);
      const bHasA = a.el === b.el ? b.kind !== 'text' : b.el.contains(a.el);
      if ((aHasB && a.kind === 'box') || (bHasA && b.kind === 'box')) {
        // something inside a card or pill: how close does it get to the card's edge?
        const o = aHasB && a.kind === 'box' ? a : b, c = o === a ? b : a;
        g = Math.min(c.r.left - o.r.left, o.r.right - c.r.right, c.r.top - o.r.top, o.r.bottom - c.r.bottom);
        if (c.kind === 'text') g += 2;   // a text box includes half-leading above and below the glyphs
      } else if (aHasB || bHasA) {
        const o = aHasB ? a : b, c = o === a ? b : a;
        if (o.kind !== 'line') continue;  // text inside plain text
        g = gap(o.r, c.r);
        if (c.kind === 'text') g += 2;
      } else {
        g = gap(a.r, b.r);
        if (a.kind === 'text' && b.kind === 'text') {
          if (g >= 0) continue;           // separate text blocks only matter if they overlap
        } else if (a.kind === 'text' || b.kind === 'text') g += 2;
        const inl = e => getComputedStyle(e).display.startsWith('inline') && !/kbd|badge|pill|toggle|chip/.test(e.className);
        if (inl(a.el) && inl(b.el) && g >= 0) continue;
      }
      if (g >= 4) continue;
      const k = a.kind + ' ' + name(a.el) + ' <> ' + b.kind + ' ' + name(b.el);
      if (tseen.has(k)) continue; tseen.add(k);
      out.touch.push(k + '  gap=' + g.toFixed(1) + 'px');
    }
  });
  return out;
}
"""


def main():
    total = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for name in PAGES:
            modes = [(w, h, "screen") for w, h in SIZES]
            if name == "logic-pro-crash-course.html":
                modes.append((794, 1123, "print"))
            if name == "logic-pro-crash-course-page.html":
                modes += [(w, h, "search:what is a region") for w, h in SIZES] + [(1280, 900, "search:make a beat")]
            for w, h, media in modes:
                query = media.split(":", 1)[1] if media.startswith("search:") else None
                pg = b.new_page(viewport={"width": w, "height": h})
                pg.emulate_media(media="print" if media == "print" else "screen")
                pg.goto((DIST / name).as_uri())
                pg.wait_for_timeout(1500)  # let the fade-in finish
                pg.evaluate("document.documentElement.classList.remove('js'); document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))")
                if query:
                    pg.evaluate("q => window.lpSearch(q)", query)
                    pg.wait_for_timeout(200)
                    pg.evaluate("window.scrollTo(0, 0)")
                r = pg.evaluate(JS, {})
                n = len(r["grey"]) + len(r["touch"])
                total += n
                print(f"\n== {name} @ {w}px {media}: {len(r['grey'])} grey, {len(r['touch'])} touching")
                for g in r["grey"][:25]:
                    print("  GREY  ", g)
                for t in r["touch"][:40]:
                    print("  TOUCH ", t)
                pg.close()
        b.close()
    print(f"\n{total} issue(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
