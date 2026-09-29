#!/usr/bin/env python3
"""Validate the eBook content before it ships.

Checks four classes of problem that a proofread will not reliably catch:

  1. Structural   — malformed JSON, missing fields, trick count below the
                    count the cover promises.
  2. Duplication  — the same trick written twice under a different section.
  3. Contradiction— one key command claimed for two different actions, which
                    means at least one of them is wrong.
  4. Provenance   — a key command that is not in the verified registry below.
  5. Citation     — every factual trick cites the source it was checked against.

Run it before every build:  python3 validate.py
Exit status is non-zero if anything fails, so it drops straight into CI.
"""

import collections
import json
import pathlib
import re
import sys

CONTENT = pathlib.Path(__file__).parent / "content"
# The cover states the count, derived at build time, so there is no promised
# floor to police any more — only that the book is not empty.
MIN_TIPS = 1

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
    # Added in the citation pass; each is cited in the trick that uses it.
    "T": "Show Tool Menu (Apple: Key commands for Tool Menu)",
    "⌃M": "Mute/unmute selected regions (Apple: Mute and solo regions)",
    "⌘U": "Set locators by selection and enable Cycle, unrounded",
    "⌥E": "Show/hide Event Float (Apple: Event Float window)",
    "⌃⌘ (hold)": "Temporarily switch the Pointer to the Velocity tool (Apple: Edit note velocity)",
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
    cited = {}
    total = 0

    for tbl in (t for p in front["pages"] for t in p.get("tables", [])):
        for row in tbl["rows"]:
            k, action = row[0], row[1]
            keys[k.strip()].append(("front matter", action))
            if len(row) < 3 or not row[2]:
                failures.append(f"front matter: key-table row with no source: {k} {action!r}")

    # 6. beginner layer — Start Here steps, glossary and goal tags are claims too.
    for pg in front["pages"]:
        for st in pg.get("steps", []):
            if not st.get("src"):
                failures.append(f"{pg['id']}: step with no source: {st['title']!r}")
            if st.get("key"):
                keys[st["key"].strip()].append(("front matter", st["title"]))
    gloss = json.loads((CONTENT / "glossary.json").read_text())
    for e in gloss:
        if not e.get("src"):
            failures.append(f"glossary: no source for {e['term']!r}")
    goal_ids = {g["id"] for g in json.loads((CONTENT / "goals.json").read_text())}

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
                if not tip.get("goals") or tip.get("lvl") not in (1, 2, 3):
                    failures.append(f"S{s['number']}: no goal/level tag: {tip['t']!r}")
                for g in tip.get("goals", []):
                    if g not in goal_ids:
                        failures.append(f"S{s['number']}: unknown goal {g!r} on {tip['t']!r}")
                cited[(f"S{s['number']}", tip["t"])] = bool(tip.get("src"))
                if tip.get("k"):
                    keys[tip["k"].strip()].append((f"S{s['number']}", tip["t"]))
                # 5. citation — a trick that states a fact about Logic must say where
                #    that fact comes from. Pure workflow advice is marked "advice".
                if not tip.get("advice"):
                    srcs = tip.get("src") or []
                    if not srcs:
                        failures.append(f"S{s['number']}: no source cited: {tip['t']!r}")
                    for src in srcs:
                        if not str(src.get("url", "")).startswith("https://"):
                            failures.append(f"S{s['number']}: bad source url on {tip['t']!r}")
                        if re.search(r"/(10\.[0-9])/", str(src.get("url", ""))):
                            warnings.append(f"S{s['number']}: cites a pre-11 Apple page: {tip['t']!r}")

    # 1. structural
    if total < MIN_TIPS:
        failures.append(f"only {total} tricks")

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
    # A key is "cited" when every trick that uses it carries a source. That is
    # the measure that matters now; the registry above is a second, older guard.
    cited_keys = {k for k, uses in keys.items()
                  if all(where == "front matter" or cited.get((where, t)) for where, t in uses)}
    print(f"key commands on cited tricks: {len(cited_keys)}/{len(keys)}")

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
