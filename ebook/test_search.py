#!/usr/bin/env python3
"""Search smoke test for the web library.

Loads dist/logic-pro-crash-course-page.html in headless Chromium, types the
kind of thing a beginner actually types, and checks that the top results are
about that thing. A query that returns nothing, or whose top three results do
not mention what was asked for, fails.

  python3 test_search.py          # needs: pip install playwright
"""

import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(__file__).parent / "dist" / "logic-pro-crash-course-page.html"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# query -> a regex at least one of the top 3 result titles must match
CASES = {
    "record vocals": r"record|vocal|take|punch|comp",
    "how do I record my guitar": r"record|input|monitor|take",
    "make a beat": r"drum|beat|step|pattern|drummer",
    "drums": r"drum",
    "fix timing": r"quanti|time|timing|groove",
    "quantise": r"quanti",
    "quantize": r"quanti",
    "autotune": r"pitch|tun",
    "tune my vocals": r"pitch|tun|vocal",
    "louder": r"loud|gain|volume|compress|level",
    "export mp3": r"bounce|export|share",
    "bounce": r"bounce",
    "change the tempo": r"tempo",
    "bpm": r"tempo",
    "loop a section": r"loop|cycle|repeat",
    "chords": r"chord",
    "piano roll": r"piano roll",
    "undo": r"undo|history",
    "save": r"save|backup",
    "reverb": r"verb|space|send|aux",
    "sidechain": r"side|chain|duck|compress",
    "split stems": r"stem",
    "sample": r"sampl",
    "chop a sample": r"sampl|slice|chop",
    "metronome": r"metronome|click",
    "headphones": r"headphone|monitor|cue",
    "keyboard shortcuts": r"key command|shortcut|key",
    "automation": r"automat",
    "hi hat": r"hi-hat|hat|drum|note repeat",
    "session player": r"session player|drummer|bass|keyboard",
    "reverbe": r"verb|space|send|aux",
    "mix": r"mix",
    "latency": r"latency|buffer|monitor",
    "delete a region": r"delete|region|remove",
    "cut a region": r"split|cut|region|scissor|trim",
    "count in": r"count",
    "melody": r"melod|note|chord|piano|step|synth|pattern",
    "⌘K": r"musical typing|keyboard",
    "play without a keyboard": r"keyboard|musical typing",
    "how do i add a track": r"track",
    "export my song": r"bounce|export|share",
    "record": r"record",
    "make it louder": r"loud|gain|volume|compress|level",
    "tempo": r"tempo",
    "pitch correction": r"pitch|tun",
}


def main():
    fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(PAGE.as_uri())
        for q, want in CASES.items():
            titles = pg.evaluate("q => window.lpSearch(q)", q)
            top = titles[:3]
            ok = bool(titles) and any(re.search(want, t, re.I) for t in top)
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {q!r:30} {len(titles):3} results  top: {top[:3]}")
        b.close()
    print(f"\n{len(CASES) - fails}/{len(CASES)} queries passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
