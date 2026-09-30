# Accuracy log

What has been checked, how, and what is still open. Newest first.

## Status

| Check | State |
| --- | --- |
| Every factual trick cites a source (enforced by `validate.py`) | Done, 249/249 |
| No contradictory or unknown key commands (enforced by `validate.py`) | Done, 47/47 keys on cited tricks |
| Claims checked against Apple's documentation through search results | Done, all tricks |
| Claims checked against the **full text** of Apple's pages | **Not done**: `support.apple.com` is blocked from the build environment. Allow it under Network access and re-run. |
| Hands-on test in Logic Pro 12 (`build_test_sheet.py`, the Logic Test Run page) | **Not started**: no results recorded yet |

The book is not yet verified hands-on. Do not describe it as "tested on Logic Pro 12" until the
test run is complete.

## 2026-09-30 — old-guide citations and the Logic Pro 12 section

Method: web search restricted to support.apple.com (the only route to Apple's text available
here), read against each trick's claim.

**The 19 tricks citing Apple's Logic 10.7 guide.** All 19 claims re-confirmed against Apple's
documentation. Apple's search index still serves the 10.7 pages for most of these topics, so
those citations stay; current-guide pages were added where search returned one. Five
corrections came out of it:

1. *Allow Quick Punch-In* (S01): Apple says it is **on by default** and recommends leaving it
   on. The trick told readers to turn it on. Retitled "Leave Allow Quick Punch-In on" and
   rewritten.
2. *Freeze the instrument* (S04): added Apple's caveat that frozen instrument tracks can
   increase disk load (Avoid system overloads, support.apple.com/en-us/108295).
3. *⌘ is your secondary tool* (S07), 4. *Make Marquee your ⌘-click tool* (S09),
5. *Marquee automation* (S09): the current guide says the Command-click Tool menu exists only
   when **Enable Complete Features** is on. Added to all three.

**Logic Pro 12 section (S19).** Confirmed: release 28 January 2026, Apple silicon and
macOS 15.6 or later; Synth Player styles (808 Bass, Pump Bass, Sequenced Bass; Rhythmic
Chords, Modulated Pad, Simple Pad) and the Alchemy default; Chord ID on audio and MIDI regions;
Mastering Assistant characters, Transparent as the default, and Transparent, Punch and Valve
needing Apple silicon; sound-pack preview and Manage Packs.

From the Logic Pro 12.2 release notes:

- Added a trick: the Legacy Patches, Legacy Instruments and Legacy Loops packs that restore
  content missing from Logic Pro 12.0.
- *⌥-drag a note to duplicate it* (S05): noted that 12.2 fixed Piano Roll notes ignoring
  "Limit Dragging to One Direction".
