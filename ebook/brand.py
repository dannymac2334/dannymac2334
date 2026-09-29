"""The dannny mcccarthy brand kit, shared by the book, the library and the sales page.

Everything here is lifted from the rates document (rates-direct.html): the
Figtree faces it embeds, the signature it opens and closes on, and its colour
and spacing tokens. The three builders import from this one place so they
cannot drift from each other or from the rates page.

  fonts/figtree-{400..800}.woff2   the exact subsets the rates page embeds
  brand/signature.png              black signature on transparent; invert on black
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).parent
WEIGHTS = ["400", "500", "600", "700", "800"]

TOKENS = {
    "paper": "#fdfdfd",
    "black": "#000",
    "ink": "#0a0a0a",
    "white": "#fff",
    # No grey text anywhere: copy is pure white on black and ink on paper.
    # Hierarchy comes from size and weight, never from a lighter colour.
    "muted_dark": "#fff",      # body copy on black
    "muted_light": "#0a0a0a",  # body copy on paper
    "line_dark": "rgba(255,255,255,.18)",
    "line_light": "rgba(0,0,0,.14)",
    "kicker": "currentColor",  # kickers and labels take the surface's text colour
    "label": "currentColor",
    "ease": "cubic-bezier(.22,.61,.36,1)",
}

FONT_STACK = '"Figtree","Helvetica Neue",Helvetica,Arial,sans-serif'


def _b64(path):
    return base64.b64encode((ROOT / path).read_bytes()).decode()


def font_faces(display="swap"):
    return "".join(
        "@font-face{font-family:'Figtree';font-style:normal;font-weight:%s;font-display:%s;"
        "src:url(data:font/woff2;base64,%s) format('woff2')}" % (w, display, _b64(f"fonts/figtree-{w}.woff2"))
        for w in WEIGHTS)


def signature_uri():
    return "data:image/png;base64," + _b64("brand/signature.png")


def root_vars():
    t = TOKENS
    return (":root{"
            f"--paper:{t['paper']};--black:{t['black']};--ink:{t['ink']};--white:{t['white']};"
            f"--muted-dark:{t['muted_dark']};--muted-light:{t['muted_light']};"
            f"--line-dark:{t['line_dark']};--line-light:{t['line_light']};"
            f"--kicker:{t['kicker']};--label:{t['label']};"
            f"--font:{FONT_STACK};--pad:clamp(20px,5.5vw,90px);--maxw:1360px;--ease:{t['ease']}"
            "}")


def signature_img(cls="sig"):
    return f'<img class="{cls}" src="{signature_uri()}" alt="Danny McCarthy signature">'
