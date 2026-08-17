#!/usr/bin/env python3
"""Finish the printed PDF so it stands on its own as a shared file.

Chromium's print pipeline carries the contents links across but does not add
a bookmark outline, and it stamps its own user agent into the metadata. Both
matter once the file leaves this repo and is opened by someone else, so this
step:

  1. builds a PDF outline (the sidebar in Preview, Acrobat and most readers)
     from the destinations the contents page already points at, and
  2. replaces the document metadata with real title/author/subject fields.

Run after the Chromium print step:  python3 finish_pdf.py
"""

import json
import pathlib
import re
import sys

import pikepdf

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
PDF = ROOT / "dist" / "logic-pro-crash-course.pdf"

AUTHOR = "Dannny McCcarthy"


def labels():
    """Map each anchor id to its outline label, so bookmarks are matched by
    name rather than inferred from page order."""
    front = json.loads((CONTENT / "00-front.json").read_text())
    out = {p["id"]: p["label"] for p in front["pages"]}
    secs = sorted(
        (json.loads(p.read_text()) for p in CONTENT.glob("[0-9][0-9].json")),
        key=lambda s: s["number"],
    )
    for s in secs:
        base = re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-")
        out[f"s{s['number']:02d}-{base}"] = f"{s['number']:02d}  {s['title']}"
    return out, len(secs), sum(len(g["tips"]) for s in secs for g in s["groups"])


def dest_page(pdf, annot, page_index):
    """Resolve a link annotation to (name, zero-based page index).

    Chromium writes anchor links as named destinations held in the old-style
    /Root/Dests dictionary, so a link's /Dest is a Name that has to be looked
    up there before it yields a page.
    """
    dest = annot.get("/Dest")
    if dest is None:
        action = annot.get("/A")
        if action is not None and action.get("/S") == "/GoTo":
            dest = action.get("/D")
    if dest is None:
        return None, None

    name = None
    if isinstance(dest, pikepdf.Name):
        name = str(dest).lstrip("/")
        dests = pdf.Root.get("/Dests")
        if dests is None or dest not in dests:
            return name, None
        dest = dests[dest]

    try:
        target = dest[0]
    except (TypeError, IndexError):
        return name, None

    for i, page in enumerate(pdf.pages):
        if page.obj == target:
            return name, i
    return name, None


def main():
    if not PDF.exists():
        print(f"missing {PDF} — run the Chromium print step first")
        return 1

    pdf = pikepdf.open(PDF, allow_overwriting_input=True)
    names, section_count, tip_count = labels()

    # Resolve every internal link to (anchor name -> page), then look the label
    # up by name so a bookmark can never point at the wrong section.
    found = {}
    for i, page in enumerate(pdf.pages):
        for annot in page.get("/Annots", []) or []:
            if annot.get("/Subtype") == "/Link":
                name, idx = dest_page(pdf, annot, i)
                if name and idx is not None:
                    found[name] = idx

    missing = [k for k in names if k not in found]
    if missing:
        print(f"  WARN  no link target found for: {', '.join(missing)}")

    entries = sorted(
        ((found[k], names[k]) for k in names if k in found),
        key=lambda pair: pair[0],
    )

    with pdf.open_outline() as outline:
        outline.root.clear()
        outline.root.append(pikepdf.OutlineItem("Cover", 0))
        for page_index, label in entries:
            outline.root.append(pikepdf.OutlineItem(label, page_index))

    with pdf.open_metadata() as meta:
        meta["dc:title"] = "Logic Pro Crash Course"
        meta["dc:creator"] = [AUTHOR]
        meta["dc:description"] = (
            f"{tip_count} Logic Pro tricks across {section_count} sections."
        )
        meta["pdf:Keywords"] = (
            "Logic Pro, music production, key commands, workflow, "
            "mixing, MIDI, recording"
        )
        meta["xmp:CreatorTool"] = AUTHOR

    # docinfo is what most readers show in Get Info / Properties.
    pdf.docinfo["/Title"] = "Logic Pro Crash Course"
    pdf.docinfo["/Author"] = AUTHOR
    pdf.docinfo["/Subject"] = (
        f"{tip_count} Logic Pro tricks across {section_count} sections."
    )
    pdf.docinfo["/Creator"] = AUTHOR

    # Open on the contents page with the bookmark sidebar showing.
    pdf.Root["/PageMode"] = pikepdf.Name("/UseOutlines")

    pdf.save(PDF, linearize=True)
    print(f"outline: {len(entries) + 1} bookmarks   metadata: set   pages: {len(pdf.pages)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
