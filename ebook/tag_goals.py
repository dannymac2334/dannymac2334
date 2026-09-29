#!/usr/bin/env python3
"""Tag every trick with the beginner goals it serves and a difficulty level.

Goals drive search-by-intent on the site and the "I want to…" index in the
PDF; level 1 marks the tricks a first-timer can use straight away. Tags are
classification, not claims about Logic, so they are derived from each trick's
own verified text: a section default plus keyword rules, capped at four.

Rerun after content changes:  python3 tag_goals.py [--apply]
Hand overrides live in OVERRIDES below and always win.
"""
import json, pathlib, re, sys, collections

CONTENT = pathlib.Path(__file__).parent / "content"

SECTION_GOALS = {1: ["start", "performance"], 2: ["arrange"], 3: ["fast"], 4: ["record-midi", "chords"],
                 5: ["edit"], 6: ["record-audio"], 7: ["edit"], 8: ["edit"], 9: ["edit"], 10: ["automation"],
                 11: ["beat"], 12: ["beat"], 13: ["beat"], 14: ["sample"], 15: ["mix"], 16: ["effects"],
                 17: ["fast"], 18: ["new"], 19: ["new"]}
RULES = [  # (goal, regex over title + body)
 ("timing", r"quantiz|quantis|groove|timing|off[- ]beat|flex time|tempo"),
 ("pitch", r"pitch correction|flex pitch|in tune|out of tune|tuning|\bpitch\b"),
 ("effects", r"reverb|delay|\beq\b|channel eq|compress|saturat|chromaglow|distortion|phat fx|chromaverb|plug-?in"),
 ("export", r"\bbounce|export|share"),
 ("loop", r"\bloop|cycle|repeat"),
 ("mix", r"\bvolume|\blevel|\bpan\b|mixer|\bsend|\baux\b|\bbus\b|fader|solo|mute"),
 ("record-audio", r"record|punch|take|microphone|\bmic\b|input monitoring|count-in|metronome"),
 ("record-midi", r"midi|musical typing|keyboard|software instrument|step input"),
 ("beat", r"\bdrum|\bbeat\b|kick|snare|hi-?hat|drummer|step sequencer|pattern|\bpad\b"),
 ("chords", r"\bchord|scale|\bkey\b|melod|arpeggi|transpos|harmon"),
 ("stems", r"\bstem"),
 ("sample", r"sampl|\bslice"),
 ("safety", r"\bsave\b|backup|back up|undo|revert|alternative|archive"),
 ("performance", r"buffer|latency|overload|\bcpu\b|freeze|crackl|thread"),
 ("organize", r"colou?r|\bname\b|rename|marker|track stack|folder|summing stack|template"),
 ("fast", r"key command|shortcut|⌥k|one keystroke|without the mouse"),
 ("automation", r"automation"),
 ("edit", r"\bcut\b|split|trim|copy|join|\bmove\b|duplicate|delete|marquee|nudge|resize|fade"),
 ("arrange", r"arrangement|section|verse|chorus|song order|insert silence"),
]
ADVANCED = r"\baux\b|\bbus\b|multithread|process buffer|alias|scripter|modifier midi|routing|sample rate|bit depth|" \
           r"flex|summing stack|environment|pre-fader|region automation|q-range|midi fx|articulation|transient"
# Reviewed by hand. Level 1 is what a first-timer should meet first; the
# keyword rules over- and under-shoot, so these win.
OVERRIDES = {
 # first-day essentials
 "1/Hit ⌘S often": {"lvl": 1}, "1/Show help tags": {"lvl": 1},
 "4/Capture the last thing you played": {"lvl": 1}, "4/Draw notes with the Pencil": {"lvl": 1},
 "6/Record‑enable multiple tracks": {"lvl": 1}, "6/Name the track before you record": {"lvl": 1},
 "9/Play just the marquee selection": {"lvl": 1}, "9/Make Marquee your": {"lvl": 1},
 "17/⌘B bounces the project": {"lvl": 1},
 "18/Flashback Capture retrieves": {"lvl": 1}, "18/Make an instrumental with one preset": {"lvl": 1},
 # not first-day
 "9/Use marquee to create a drop": {"lvl": 2}, "18/Set the Bass Player to follow": {"lvl": 2},
 "18/Resize chords by dragging": {"lvl": 2}, "18/Generate chords from an existing region": {"lvl": 2},
 "18/Convert to MIDI, then thin out": {"lvl": 2}, "8/Move a comp edit point": {"lvl": 2},
 "8/Add a tiny fade": {"lvl": 2}, "8/Remove Silence": {"lvl": 2}, "8/Curve the fade": {"lvl": 2},
 "8/Audio File Editor": {"lvl": 3}, "16/side‑chain filter": {"lvl": 3}, "16/ChromaVerb": {"lvl": 2},
 "5/Event Float": {"lvl": 2}, "5/Force legato": {"lvl": 2}, "2/Make a folder out of a section": {"lvl": 2},
 "15/Drag plugins between insert slots": {"lvl": 2}, "19/Run Chord ID on your own old bounces": {"lvl": 2},
 "13/Every pad is its own channel strip": {"lvl": 2}, "7/⌘ is your secondary tool": {"lvl": 2},
 # settings pages: most are tuning, not day-one
 "1/buffer": {"lvl": 3}, "1/Threads": {"lvl": 3}, "1/Multithreading": {"lvl": 3},
 "1/Software Monitoring": {"lvl": 3}, "1/MIDI Reset": {"lvl": 3}, "1/doubled notes": {"lvl": 3},
 "1/sample rate": {"lvl": 3}, "1/bit depth": {"lvl": 3}, "1/Smart Tempo": {"lvl": 3},
 "1/pre-quantised": {"lvl": 3}, "1/Tuning": {"lvl": 3}, "1/Sound Library": {"lvl": 3},
 "1/assets": {"lvl": 3}, "1/channel strip as a setting": {"lvl": 3}, "1/Limit Dragging": {"lvl": 3},
 "1/Clean Up": {"lvl": 3}, "1/Auto Set Locators": {"lvl": 3},
}


def tag(n, t):
    text = (t["t"] + " " + t["d"]).lower()
    goals = list(SECTION_GOALS.get(n, []))
    for g, rx in RULES:
        if re.search(rx, text) and g not in goals:
            goals.append(g)
    goals = goals[:4]
    body = t["d"]
    if re.search(ADVANCED, text):
        lvl = 3 if len(re.findall(ADVANCED, text)) > 1 else 2
    elif len(body) <= 230 and (t.get("k") or re.search(r"\bpress\b|\bclick\b|\bchoose\b|\bdrag\b", text)):
        lvl = 1
    else:
        lvl = 2
    for frag, o in OVERRIDES.items():
        sec, title = frag.split("/", 1)
        if int(sec) == n and title.lower() in t["t"].lower():
            goals = o.get("goals", goals); lvl = o.get("lvl", lvl)
    return goals, lvl


def main(apply):
    dist = collections.Counter(); lv = collections.Counter(); starters = []
    for p in sorted(CONTENT.glob("[0-9][0-9].json")):
        s = json.loads(p.read_text()); n = s["number"]
        for g in s["groups"]:
            for t in g["tips"]:
                goals, lvl = tag(n, t)
                t["goals"], t["lvl"] = goals, lvl
                dist.update(goals); lv[lvl] += 1
                if lvl == 1: starters.append((n, t["t"]))
        if apply:
            p.write_text(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
    print("levels:", dict(sorted(lv.items())))
    print("goals:", dict(dist.most_common()))
    return starters

if __name__ == "__main__":
    st = main("--apply" in sys.argv)
    if "--list" in sys.argv:
        for n, title in st: print(f"  S{n:<2} {title}")
