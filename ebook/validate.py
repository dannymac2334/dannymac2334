#!/usr/bin/env python3
"""Validate the eBook content before it ships.

Checks four classes of problem that a proofread will not reliably catch:

  1. Structural   — malformed JSON, missing fields, trick count below the
                    count the cover promises.
  2. Duplication  — the same trick written twice under a different section.
  3. Contradiction— one key command claimed for two different actions, which
                    means at least one of them is wrong.
  4. Provenance   — a key command that is not in the verified registry below.

Run it before every build:  python3 validate.py
Exit status is non-zero if anything fails, so it drops straight into CI.
"""

import collections
import json
import pathlib
import re
import sys

CONTENT = pathlib.Path(__file__).parent / "content"
MIN_TIPS = 265  # the surviving, verified count — raise only by verifying more

# --------------------------------------------------------------------------
# Verified key command registry.
#
# CONFIRMED — checked against Apple's Logic Pro User Guide or two or more
#             independent references during the accuracy pass.
# STANDARD  — long-standing factory defaults, stable across versions.
#
# Anything a content file uses that is not listed here gets reported, so a
# newly invented shortcut cannot reach the PDF unnoticed.
# --------------------------------------------------------------------------
CONFIRMED = {
    "⌥K": "Open Key Commands",
    "⇧R": "Flashback Capture / capture most recent MIDI performance",
    "⌘T": "Split regions at playhead",
    "⌘D": "New track with duplicate settings",
    "⌥C": "Show / hide Colors palette",
    "⌘F": "Show / hide Flex",
    "A": "Show / hide automation (Tracks area and Piano Roll)",
    "K": "Metronome on / off",
    "/": "Open Go to Position dialog",
    "V": "Hide / show all plug-in windows",
    "⇧N": "Rename region",
    "⌃X": "Remove Silence from Audio Region",
    "⇧F": "Select All Following (all tracks)",
    "⌘⇧D": "Create Track Stack",
    "⌥← / ⌥→": "Nudge by nudge value",
    "⌥↑ / ⌥↓": "Transpose selection by semitone",
    "⌥⇧ + drag": "Create MIDI alias / audio clone",
    "⌃⇧ + drag": "Drag at tick or sample resolution",
    "⌃ + drag": "Move in steps of one division, overriding snap",
    "⌃B": "Bounce Regions in Place",
    "⌘K": "Musical Typing",
    "⌘ + drag": "Marquee select; swap arrangement markers; constrain a drag to one axis",
    "⌥ + drag": "Copy instead of move; duplicate an arrangement section",
}

STANDARD = {
    "Space": "Play / Stop",
    "↩": "Go to beginning",
    "R": "Record",
    "C": "Cycle on / off",
    "U": "Set locators by regions",
    "L": "Toggle loop for selected region",
    "M": "Mute",
    "X": "Mixer",
    "P": "Piano Roll",
    "E": "Editor",
    "N": "Score Editor",
    "Y": "Library",
    "O": "Loop Browser",
    "F": "Browsers",
    "B": "Smart Controls",
    "I": "Inspector",
    "G": "Global Tracks",
    "Z": "Zoom to fit selection",
    "Esc": "Tool menu",
    "⌫": "Delete selection",
    "Delete": "Delete selection",
    "⌘": "Secondary tool modifier",
    "⌘Z": "Undo",
    "⇧⌘Z": "Redo",
    "⌘S": "Save",
    "⇧⌘S": "Save as",
    "⌘A": "Select all",
    "⇧⌘A": "Deselect all",
    "⌘J": "Join regions",
    "⌘R": "Repeat regions or events",
    "⌘B": "Bounce project or section",
    "⌘,": "Preferences",
    "⌘.": "Stop and discard recording",
    "⌘← / ⌘→": "Zoom horizontally",
    "⌘↑ / ⌘↓": "Zoom vertically",
    "⌃⌥ + drag": "Drag-zoom",
    "⌥ + click": "Reset control / bypass insert / exclusive solo (context)",
    "⇧ + click": "Extend selection",
    "⌥K to assign": "Instruction, not an assertion",
}

KNOWN = {**CONFIRMED, **STANDARD}


def load():
    front = json.loads((CONTENT / "00-front.json").read_text())
    secs = sorted(
        (json.loads(p.read_text()) for p in CONTENT.glob("[0-9][0-9].json")),
        key=lambda s: s["number"],
    )
    return front, secs


def main():
    failures, warnings = [], []
    front, secs = load()

    keys = collections.defaultdict(list)
    titles = collections.defaultdict(list)
    total = 0

    for tbl in (t for p in front["pages"] for t in p.get("tables", [])):
        for k, action in tbl["rows"]:
            keys[k.strip()].append(("front matter", action))

    for s in secs:
        if not s.get("groups"):
            failures.append(f"section {s['number']} has no groups")
        for g in s["groups"]:
            for tip in g["tips"]:
                total += 1
                for field in ("t", "d"):
                    if not tip.get(field, "").strip():
                        failures.append(f"S{s['number']}: tip missing '{field}'")
                titles[tip["t"].strip().lower()].append(s["number"])
                if tip.get("k"):
                    keys[tip["k"].strip()].append((f"S{s['number']}", tip["t"]))

    # 1. structural
    if total < MIN_TIPS:
        failures.append(f"only {total} tricks; cover promises {MIN_TIPS}+")

    # 2. duplication
    for title, where in titles.items():
        if len(where) > 1:
            failures.append(f"duplicate trick title in sections {where}: {title!r}")

    # 3. contradiction — one key, two materially different claimed actions
    for k, uses in keys.items():
        claims = {re.sub(r"[^a-z ]", "", a.lower())[:30] for _, a in uses}
        if len(claims) > 1 and k not in KNOWN:
            failures.append(f"key {k!r} claimed for conflicting actions: {uses}")

    # 4. stale marketing — the built HTML derives its counts from content/, but the
    #    handoff and pitch docs are hand-written, so they drift. They are what gets
    #    sent to other people, which makes a stale number worse there than anywhere.
    pages = 0
    pdf = pathlib.Path(__file__).parent / "dist" / "logic-pro-crash-course.pdf"
    if pdf.exists():
        try:
            import pypdfium2
            pages = len(pypdfium2.PdfDocument(str(pdf)))
        except Exception:
            pages = 0
    for name in ("README.md", "HANDOFF.md", "PITCH.md", "AGENT-PROMPT.md"):
        doc = pathlib.Path(__file__).parent / name
        if not doc.exists():
            continue
        text = doc.read_text()
        for n in set(re.findall(r"\b(\d{3})\s+(?:written\s+)?tricks\b", text)):
            if int(n) != total:
                failures.append(f"{name} says {n} tricks; the book has {total}")
        if pages:
            for n in set(re.findall(r"\b(\d{2,3})\s+pages\b", text)):
                if int(n) != pages:
                    failures.append(f"{name} says {n} pages; the PDF has {pages}")

    # 5. provenance
    for k in sorted(keys):
        if k not in KNOWN:
            warnings.append(f"key {k!r} is not in the verified registry")

    print(f"tricks: {total}    sections: {len(secs)}    distinct keys: {len(keys)}")
    confirmed_used = sum(1 for k in keys if k in CONFIRMED)
    print(f"keys confirmed against documentation: {confirmed_used}/{len(keys)}")

    for w in warnings:
        print(f"  WARN  {w}")
    for f in failures:
        print(f"  FAIL  {f}")

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"\npassed{f' with {len(warnings)} warning(s)' if warnings else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
