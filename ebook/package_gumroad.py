#!/usr/bin/env python3
"""Package everything the Gumroad listing and the store page need.

Run after the builds (see README). Writes:

  dist/gumroad/Logic-Pro-Crash-Course.pdf            the product files, upload both
  dist/gumroad/Logic-Pro-Crash-Course-Library.html    (git-ignored: paid content)
  dist/store/logic-pro-crash-course.png / .webp       1080x1080 store card cover
  dist/store/logic-pro-crash-course-wide.png / .webp  1920x1080 store banner
  dist/store/gumroad-cover-1280x720.png               Gumroad product cover
  dist/store/gumroad-thumb-600.png                    Gumroad thumbnail

Covers are rendered in the rates-page brand (brand.py) by headless Chromium, and
carry no price, so a price change never means redrawing them.
"""

import pathlib
import shutil

from PIL import Image
from playwright.sync_api import sync_playwright

import brand
from build import load, count_tips

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def cover_html(w, h, total, sections, versions):
    big = min(w, h)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{brand.font_faces(display="block")}{brand.root_vars()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;background:#000;color:#fff;font-family:var(--font);overflow:hidden}}
.c{{position:absolute;inset:{round(big*.085)}px;display:flex;flex-direction:column;justify-content:space-between}}
.sig{{display:block;width:{round(big*.26)}px;filter:invert(1);margin-bottom:{round(big*.045)}px}}
.k{{font-size:{round(big*.019)}px;font-weight:500;letter-spacing:.24em;text-transform:uppercase}}
h1{{margin-top:{round(big*.03)}px;font-weight:700;font-size:{round(big*(.135 if w == h else .12))}px;line-height:.94;letter-spacing:-.048em}}
.row{{display:flex;gap:{round(big*.02)}px}}
.s{{border:1px solid rgba(255,255,255,.35);border-radius:{round(big*.018)}px;padding:{round(big*.022)}px {round(big*.026)}px}}
.s b{{display:block;font-size:{round(big*.06)}px;line-height:1;letter-spacing:-.03em}}
.s span{{display:block;margin-top:{round(big*.01)}px;font-size:{round(big*.017)}px;font-weight:500;letter-spacing:.2em;text-transform:uppercase}}
</style></head><body><div class="c">
<div>{brand.signature_img()}<p class="k">{versions}</p><h1>Logic Pro<br>Crash Course.</h1></div>
<div class="row"><div class="s"><b>{total}</b><span>Tricks</span></div><div class="s"><b>{sections}</b><span>Sections</span></div><div class="s"><b>100%</b><span>Cited</span></div></div>
</div></body></html>"""


def main():
    front, sections = load()
    total = count_tips(sections)
    versions = front["edition"].replace("Covers ", "")

    g = DIST / "gumroad"
    g.mkdir(parents=True, exist_ok=True)
    shutil.copy(DIST / "logic-pro-crash-course.pdf", g / "Logic-Pro-Crash-Course.pdf")
    shutil.copy(DIST / "logic-pro-crash-course-page.html", g / "Logic-Pro-Crash-Course-Library.html")

    s = DIST / "store"
    s.mkdir(parents=True, exist_ok=True)
    shots = [("logic-pro-crash-course", 1080, 1080), ("logic-pro-crash-course-wide", 1920, 1080),
             ("gumroad-cover-1280x720", 1280, 720)]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for name, w, h in shots:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.set_content(cover_html(w, h, total, len(sections), versions))
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(s / f"{name}.png"))
            pg.close()
        b.close()
    for name in ("logic-pro-crash-course", "logic-pro-crash-course-wide"):
        Image.open(s / f"{name}.png").save(s / f"{name}.webp", quality=90)
    Image.open(s / "logic-pro-crash-course.png").resize((600, 600), Image.LANCZOS).save(s / "gumroad-thumb-600.png")

    for f in sorted(g.iterdir()) + sorted(s.iterdir()):
        print(f"  {f.relative_to(ROOT)}  ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
