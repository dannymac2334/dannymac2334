# Audit — first result

A 19-agent pass over the book: one auditor per section required to produce a URL and a
quoted line for anything it cleared, then a skeptic pass whose job was to knock those
clearances back down.

## The run did not finish

**Sections 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 were never checked.** The session's WebSearch
budget (200 calls) was consumed by sections 1–5 and the earlier manual checks. Every agent
from section 6 onward reported the same thing: first search refused, WebFetch egress-blocked
on every source domain, zero claims adjudicated. They returned `search_worked=false` and said
plainly not to act on their verdicts — which is why nothing was deleted.

That leaves **108 of 364 tricks** genuinely audited, and **256 untouched**.

## What the audited third looks like

| Verdict | Count | Share |
| --- | ---: | ---: |
| VERIFIED | 33 | 31% |
| NO_FACTUAL_CLAIM | 2 | 2% |
| UNVERIFIABLE | 35 | 32% |
| WRONG | 38 | 35% |

The skeptic pass downgraded 27 tricks the auditors had cleared.

`WRONG` does not mean unproven. It means Apple's own documentation says otherwise: a setting
that does the opposite of what the book claims, a menu item under a different menu, a command
that does not exist under the name given, a feature credited to the wrong release.

## Every WRONG finding

### S1 — Enable Multithreading on Playback Tracks

The body describes the behaviour of the wrong option. Apple states that 'Playback Tracks' hands all live/input DSP to ONE thread and one core — the exact opposite of 'it spreads live tracks across cores instead of choking one'. The setting that spreads live tracks across cores is 'Playback & Live Tracks'.

https://support.apple.com/en-us/101975

### S1 — Turn off “Allow Quick Punch‑In” only if you never punch

Two errors. (1) Location: Allow Quick Punch-In is a Record menu item (or the Record button's shortcut menu), not an item in Logic Pro > Settings > Recording where this group's path places it. (2) Key command: Apple's procedure specifies the Record Toggle key command, not R. R is the plain Record command; multiple key-command references list Record Toggle's default as the asterisk (*). The 'keeps the audio before the punch point intact' part is correct.

https://support.apple.com/guide/logicpro/punch-in-and-out-of-audio-recordings-lgcpb19bfd0d/10.7/mac/11.0

### S1 — Enable “Auto demix by channel if multitrack recording”

Version trap, and a wrong location. The option lives in File > Project Settings > Recording (a project setting), not Logic Pro > Settings > Recording as this group's path implies — and it was removed in Logic Pro 11.0.1, with 'Automatically erase duplicates' occupying its place. The book claims to cover 10.7, 11 and 12, so this trick is dead for two of the three versions and says nothing about it.

https://www.logicprohelp.com/forums/topic/156571-auto-demix-is-no-longer-an-option-in-latter-versions-of-logic/

### S1 — Turn on the pre‑roll metronome click only

Apple's Metronome project settings page confirms both checkboxes and what each does, and 'Toggle Metronome Click' is the default K key command per studio-interns.com's key-command reference. Two small notes: the settings are in File > Project Settings > Metronome, not Settings > Recording as the group path implies; and 'Click while recording' covers the count-in AND the whole recording pass, not pre-roll only, so the title slightly oversells it.

https://support.apple.com/guide/logicpro/metronome-project-settings-lgcpe1d6118e/mac

### S1 — Set the MIDI reset options to send Notes Off only

Apple's Reset Messages page gives the opposite advice: leave ALL of these unselected, which is the default, because Logic handles MIDI resets automatically. The trick tells the reader to select Control 123 (All Notes Off), which is a change away from Apple's stated recommendation, and its stated rationale ('the other resets can wipe controller states') is also backwards — Apple's point is that these legacy resets exist only for compatibility with older MIDI devices.

https://support.apple.com/guide/logicpro/reset-messages-settings-lgcp7123ac34/mac

### S1 — Turn off region colouring by track and colour by region instead

The named option does not exist. Apple's Region Color pop-up offers 'Individual' and 'As Track Color' — there is no 'As Region Colour'. A reader hunting for that entry will not find it. (Also: in current Logic the pane is Settings > View > Tracks, not Settings > Display > Tracks.)

https://support.apple.com/guide/logicpro/change-the-color-of-regions-lgcpf7c0db8c/mac

### S1 — Set Cycle to “Auto‑set locators by region selection”

The behaviour is real but the location is not. Auto Set Locators lives in the Cycle button's shortcut menu in the control bar, not in Settings > General > Cycle. Apple's actual General > Cycle settings pane contains only Cycle Pre-Processing and the Smooth Cycle Algorithm checkbox. A reader following 'General > Cycle' will not find this.

https://support.apple.com/guide/logicpro/select-parts-of-regions-lgcpf7c0ae21/mac

### S1 — Set “Limit Dragging to One Direction” to Vertically in the Tracks area

There is no 'Vertically' option to set. It is a plain checkbox — 'Limit Dragging to One Direction: In Tracks' — and its behaviour is not vertical-locking: it locks to whichever axis you start moving in, so an initial left/right move constrains you to horizontal. The trick's stated goal (not nudging a region off the grid while moving it to another track) is achieved by ticking the checkbox and then, per Apple, releasing and re-dragging to change track — or by holding Shift to override.

https://support.apple.com/guide/logicpro/move-regions-lgcpf7c0d489/mac

### S1 — Turn off “Catch playhead” while editing

The command name is real ('Catch Playhead Position', default ⌥O per studio-interns.com) and the advised workflow is correct. WORDING FIX NEEDED, not a factual failure: the opening sentence is inverted — the Catch button is what MAKES the view follow the playhead; turning it OFF is what stops the chase. Reword to 'The Catch button in each editor makes the view follow the playhead. Turn it off when you are editing a specific bar…'

https://www.studio-interns.com/2019/11/26/catch-playhead-position-logic-pro-x-keyboard-command-of-the-day/

### S1 — Set your sample rate before you record, not after

The path and the 48/44.1 guidance are right, but the stated consequence is wrong. Apple says changing the sample rate after recording causes PITCH AND PLAYBACK SPEED changes — i.e. Logic does not resample your existing files, they simply play back at the wrong speed. 'Resamples everything and softens transients' describes something Logic does not do, and it understates the damage, which is what would generate the refund email.

https://support.apple.com/guide/logicpro/set-the-project-sample-rate-lgcpce0958b8/mac

### S1 — Set the recording bit depth to 24-bit

Version error. 32-bit float recording did not arrive in Logic Pro 11.1 — it shipped in Logic Pro 10.8 in November 2023, alongside Mastering Assistant. The location claim is fine: Apple's Recording settings pane does contain the Bit Depth pop-up.

https://support.apple.com/en-us/120134

### S1 — Turn on “Bounce project settings” for consistent exports

The title names something that does not exist and does not match its own body. The body describes the Assets project settings, which Apple documents as being about portability — copying audio, samples and impulse responses into the project package — not about bouncing or export consistency. Everything after the title is correct; the title is the defect.

https://support.apple.com/guide/logicpro/manage-project-assets-lgcpce0d70e7/mac

### S1 — Turn on Project Alternatives before you need them

The menu path is wrong. It is File > Project Alternatives > New Alternative, not File > Alternatives > New Alternative. The feature and the description of it are correct. Worth adding: alternatives require Enable Complete Features to be on, which ties this to the earlier trick.

https://support.apple.com/guide/logicpro/use-project-alternatives-and-backups-lgcpa158ef77/mac

### S1 — Set autosave and then still hit ⌘S

'Set autosave' tells the reader to configure something that has no user-facing control. Logic's autosave runs invisibly and exposes no preference — the only thing you can configure is Auto Backup, which is a different feature (versions saved on each manual save, retrieved via File > Revert To). The body's advice is fine; the instruction in the title is not actionable.

https://logicstudiotraining.com/wiki/index.php/Autosave

### S1 — Set the audio file location to “Project” not “Folder”

The option is not called 'Project'. In the File > Save As dialog the two buttons are 'Organize my project as: Package' and 'Organize my project as: Folder'. The body itself says 'package' — only the title is wrong, and it is the half a reader will go hunting for.

https://support.apple.com/guide/logicpro/save-projects-lgcpce128e82/mac

### S2 — ⌘-drag one arrangement marker onto another to swap sections

The Logic Pro User Guide describes the swap as a PLAIN drag of one arrangement marker directly over another — no ⌘ modifier. Searches that did not contain the word "Command" returned this line consistently; ⌘-drag is not what the guide credits with swapping. The trick's premise that "a plain drag moves or inserts" (and therefore cannot swap) is what the guide contradicts.

https://support.apple.com/guide/logicpro/edit-arrangement-markers-lgcpf7c0a3d7/mac

### S2 — Insert silence across the whole project

The menu item is named "Insert Silence Between Locators", not "Insert Silence at Locators". A reader following the book's path will not find that command in the Edit > Cut/Insert Time submenu. The submenu name itself (Edit > Cut/Insert Time) is correct.

https://support.apple.com/en-al/guide/logicpro/lgcp21e2cb21/10.7/mac/11.0

### S2 — Snap arrangement markers to your actual section boundaries

New arrangement markers ignore the locators AND the playhead entirely — Apple states they always appear at the start of the project or after the last existing marker, at a fixed default length of eight bars. Setting locators with U before creating one changes nothing about where the marker lands, so the trick's whole payoff ("it lands perfectly instead of approximately") is false. U itself is real (Set Rounded Locators by Regions/Events and Enable Cycle) but does not feed arrangement-marker creation.

https://support.apple.com/guide/logicpro/add-arrangement-markers-lgcpb9f20ee5/mac

### S2 — Convert loops to real regions only at the very end

There is no "Loops to Regions" command in the Logic Pro User Guide. The command under Edit > Convert is "Loops to Aliases", and it does not produce independent real regions for MIDI — it produces aliases (audio loops become cloned regions). Two separate searches for "Loops to Regions" both returned the guide's "Loops to Aliases" wording and no such command by the book's name.

https://support.apple.com/guide/logicpro/loop-regions-lgcpf7c0e0db/10.7/mac/11.0

### S2 — Solo an arrangement section with the locators

Two problems. (1) U is "Set Rounded Locators by Regions/Events and Enable Cycle" — it turns Cycle mode ON by itself, so pressing C afterwards toggles Cycle back OFF and you end up NOT looping. (2) Apple's arrangement-marker pages document clicking a marker as selecting the marker (Shift-click for several), not as selecting the regions beneath it; no such region-selection behaviour is documented.

https://support.apple.com/guide/logicpro/use-the-cycle-area-lgcp59e41e86/10.7/mac/11.6.2

### S2 — Mute regions instead of deleting them while experimenting

The region-mute key command is Control-M, not M. Apple's Mute and solo regions page gives Control-M and the Mute tool as the two ways to mute/unmute selected regions; plain M is the track-mute command, which mutes the whole track rather than the selected regions — exactly the adjacent-but-different error the book must avoid.

https://support.apple.com/guide/logicpro/mute-and-solo-regions-lgcp2217b80d/mac

### S3 — Toggle Catch to stop the screen running away

The description of Catch is right — Apple: "The Catch playhead setting makes the visible section of a window follow the playhead position" — but the advice to "search 'Catch Playhead Position' in Key Commands to put it on a key", reinforced by the ⌥K badge, tells the reader it has no default key. It does. studio-interns.com's keyboard-command-of-the-day entry is titled "Catch Playhead Position `", and the same backquote assignment appears in independent shortcut references (shortcutfoo.com, gieson.com). A buyer who searches Key Commands will find the command already bound and conclude the book is wrong.

https://www.studio-interns.com/2019/11/26/catch-playhead-position-logic-pro-x-keyboard-command-of-the-day/

### S4 — Musical Typing turns your laptop into a synth

Apple's user guide confirms all four mappings exactly: ⌘K to open, Z/X for octaves, C/V for velocity, Tab for sustain. One wording nit for the owner: Apple describes Tab as a TOGGLE ('turn sustain on or off'), whereas the copy says the key 'holds' sustain. The mapping is right; 'toggles sustain (like a sustain pedal)' would be more precise.

https://support.apple.com/guide/logicpro/play-software-instruments-lgcpb19cbd34/mac

### S4 — Capture the last thing you played, even when not recording

⇧R and the Logic 11.2 requirement for audio both check out, but the stated prerequisite is wrong. Apple's requirement for audio Flashback Capture is that the audio track be IN FOCUS — not record-enabled. Apple's page never mentions record-enabling; the conditions are focus, the project playing, and an incoming signal (plus a four-second minimum). logicstudiotraining.com independently describes it the same way ('capture audio on the focused track whenever the project is playing and an audio signal is present'). A buyer who record-arms a track and finds it still doesn't work — or who assumes arming is required and never tries it otherwise — has a legitimate complaint.

https://support.apple.com/guide/logicpro/capture-a-recent-audio-performance-lgcpa5d2f9b8/mac

### S4 — Draw notes with the Pencil, delete with the Eraser

Two problems. (1) 'The Pencil creates notes at the current division' contradicts Apple, which says a new note takes the length/velocity/channel of the previously created or edited note — and it contradicts the very next trick in this same book. (2) Apple's Delete notes page enumerates the deletion methods and Pointer double-click is not among them; the double-click-to-delete behaviour that Logic users actually report is with the Pencil tool, not the Pointer. Classic wrong-tool attribution. The ⌥-drag clause is fine, though Apple describes it as copying a note to a new position rather than 'at the same pitch'.

https://support.apple.com/guide/logicpro/delete-notes-lgcpa9100075/mac

### S4 — New notes inherit the last note you touched

Apple's current Mac guide states the inheritance behaviour verbatim, which is exactly the hi-hat workflow the trick describes. Small nuance the owner may want to soften: Apple also documents a Control-click 'Define as Default Note' command and a fresh-project default of 240 ticks / velocity 80 / channel 1, so 'there is no default-velocity field' is true of the UI but slightly overstates the absence of any default mechanism.

https://support.apple.com/guide/logicpro/add-notes-lgcpa904cb3a/mac

### S4 — Use the Chord Trigger MIDI plugin to play chords with one finger

The plug-in and the one-finger premise are right, but the Learn sequence is backwards. Apple's documented order is: click Learn, then pick the TRIGGER KEY on the upper keyboard first, then enter the chord notes on the lower keyboard. The book says hit Learn, play the chord, then assign it to a key. A reader following the printed order will not get a chord assignment.

https://support.apple.com/guide/logicpro/use-chord-trigger-lgce9d7955e9/mac

### S4 — Force everything into key with Transposer's scale quantize

Transposer does correct notes to a scale in real time, but there is no 'scale quantize' control to turn on. Apple's controls page enumerates the whole plug-in — Transpose slider, Root pop-up, Scale pop-up, and the on-screen Keyboard for building a User scale — and there is no scale-quantize switch. Choosing the Root and Scale IS the mechanism. A reader hunting for a button that doesn't exist is exactly the kind of small wrongness that reads as sloppy.

https://support.apple.com/guide/logicpro/transposer-midi-plug-in-controls-lgceee5a5e6f/mac

### S4 — Use Arpeggiator to generate parts, then commit them

Bounce in Place does not produce editable notes — it produces audio. Apple is explicit that it renders selected regions to a 24-bit audio file at the project sample rate. The trick offers Bounce in Place and 'record its output to another track' as two routes to the same result ('editable notes'), and only the second one yields MIDI. A buyer who bounces in place expecting an editable MIDI region gets an audio file instead.

https://support.apple.com/guide/logicpro/bounce-in-place-overview-lgcpe2a9f868/mac

### S4 — Use the Modifier MIDI plugin to remap anything to anything

'Velocity into CV' is not a thing Modifier can do — CV (control voltage) is not a MIDI event type in Logic at all. Apple scopes the plug-in tightly: it reassigns or filters a SINGLE continuous controller or fader event, which also makes 'remap anything to anything' an overclaim. The modwheel-to-aftertouch and pitchbend-to-expression examples are within scope; the CV example is not.

https://support.apple.com/guide/logicpro/modifier-controls-lgce0604d2d0/mac

### S4 — Use Note Repeat for hi‑hats and rolls

Note Repeat in Logic Pro for Mac is a per-step Step Sequencer EDIT MODE — you drag vertically on a step to slice it into 1–16 repeats. It is not a live 'hold a note and it rolls' performance function, and Apple's Drum Machine Designer pad-controls documentation contains no Note Repeat feature at all, so 'or from the drum pad controls' is unsupported on Mac. The hold-to-roll behaviour the trick describes is how note repeat works on hardware pads and in Logic Pro for iPad, not in the Mac app the book covers — a textbook version/platform mix-up.

https://support.apple.com/guide/logicpro/use-edit-modes-lgcpf8b9a06c/mac

### S5 — Change note length numerically in the inspector

Wrong UI element. Apple describes the Piano Roll Editor inspector as holding quantize/pitch/velocity controls, not a position/length/channel event display. The window that shows Position, Status, Channel, Number (pitch), Velocity and Length for a selected event is the Event Float (⌥E) — and Apple documents no multi-note simultaneous typing there either, so that part of the claim is dropped from the correction.

https://support.apple.com/guide/logicpro/event-float-window-lgcp2158f388/mac

### S5 — Force legato to fix gappy pads

The Edit > Trim submenu exists in the Piano Roll, but there is no item called "Note Force Legato". Every command in that submenu is named "Note End to ..."; the force-legato one is "Note End to Following Notes (Force Legato)". A buyer following the book's path will not find the menu item.

https://9to5mac.com/2016/02/21/logic-pros-how-to-solo-tricks-edit/

### S5 — Trim overlaps automatically

There is no Edit > Trim > "Note Overlaps" command. Apple's list of Piano Roll Trim commands names the overlap-removal ones "Note End to Remove Overlaps to Selected Notes / Following Notes / Repeated Notes (8 Ticks Gap)" — and they leave an eight-tick gap, which the book's description does not mention.

https://support.apple.com/guide/logicpro/resize-notes-lgcpa90a4474/mac

### S5 — ⌥‑drag a note to duplicate it

The ⌥-drag-to-copy half is correct and documented by Apple. The Shift half is the classic "adjacent behaviour" error: Shift while dragging toggles Logic's "Limit Dragging to One Direction In Piano Roll and Score" behaviour — it restricts you to whichever direction you started dragging in, which only preserves pitch if you happened to start horizontally. It is not a pitch lock, and pitch-constrained dragging is a Settings option, not a modifier.

https://support.apple.com/guide/logicpro/move-notes-lgcpa905f117/mac

### S5 — Place a note between grid divisions

The ⌃⌥-drag warning is correct — that gesture is the Zoom tool. But Logic's Snap pop-up menu has no "off" setting: the options are Smart, Bar, Beat, Division, Ticks, Frames and Samples. The documented way to escape the grid mid-drag is Control-Shift, which moves notes in tick steps and overrides the Snap value.

https://support.apple.com/guide/logicpro/move-notes-lgcpa905f117/mac

### S5 — Change velocity by dragging with the Velocity tool

The tool and the drag are documented exactly as written, but the colour claim is not true by default: Apple says velocity is shown by the length of the horizontal line inside each note, and colour-by-velocity is an opt-in View setting. A reader who tries this with default settings will see a help tag and a line change, not a colour change.

https://support.apple.com/guide/logicpro/edit-note-velocity-lgcpa8fee137/mac

### S5 — Use Q‑Range to leave close notes alone

Apple's description of positive Q-Range values matches the trick exactly. Worth flagging for the owner, though it does not make the trick wrong: negative Q-Range values invert the behaviour, so a one-clause aside such as "use positive values" would remove any ambiguity.

https://support.apple.com/guide/logicpro/advanced-quantization-parameters-lgcp35029a2b/mac

## Could not be confirmed either way

Not necessarily false — simply unsupported by any source reachable from here.

- **S1 — Turn on Low Latency Mode and give it a key command** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple's 'Work with plug-in latencies' page confirms the mechanism precisely (bypasses latency-inducing plug-ins on record-enabled/input-monitored tracks), and Apple's key commands page confirms ⌥K opens the Key Commands window where you would assign it.
- **S1 — Set the count‑in to 1 bar, not 2** *(cleared by the auditor, downgraded by the skeptic)*  
  The only checkable assertion — that the count-in length is settable in bars — holds. macProVideo documents choosing count-in length in bars from the count-in button, and the count-in also has a dedicated Record > Count In submenu. '1 bar not 2' is taste. FLAG: this trick sits under the group path 'L
- **S1 — Set MIDI recording to “Create Take Folder”** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple's Recording settings page confirms both the location and the result. Minor wording note for the owner: the control is the 'MIDI Cycle On' pop-up inside the 'Overlapping Track Recordings' area of Settings > Recording, not a sub-pane called 'Recording > MIDI'.
- **S1 — Set the click source to a sound you can actually hear**  
  The 'set the accented downbeat louder' half is sourced (per-event velocity fields for bar/beat/division). The 'swap the default woodblock for a rimshot or cowbell' half is not: Apple documents no sound-picker for the click. The click is the Klopfgeist plug-in on the Click channel strip, whose charac
- **S1 — Enable “Display middle C as C3”** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple documents the pop-up menu, both options, and the location. Only nit: it is a pop-up menu with C3 (Yamaha) / C4 (Roland), not a checkbox to 'enable', and in current Logic the pane is Settings > View > General (it was Settings > Display > General in 10.7).
- **S1 — Set the maximum undo steps to 100+** *(cleared by the auditor, downgraded by the skeptic)*  
  The setting exists where the trick says it does, and 100+ is achievable — Apple documents a ceiling of 200, so the advice is inside the possible range.
- **S1 — Set a default channel strip for new tracks**  
  Apple documents saving a channel strip setting (via the Setting button > Save Channel Strip Setting As) and browsing settings in the Library, but I could not find the 'control-click in the Library > Set as default' step in Apple's guide or in two independent reputable educators — only a single blog,
- **S1 — Set the default region colour palette**  
  The key command is solid — Apple documents Option-C as the way to open the Color palette, and documents double-clicking a swatch to define a custom colour. What I cannot verify anywhere is the trick's actual promise: that you can 'rearrange' the palette once and get consistent colours 'across every 
- **S2 — Repeat regions numerically instead of dragging** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple documents Edit > Repeat Multiple with a Number of Copies field and a copies-vs-aliases choice; Why Logic Pro Rules confirms ⌘R as the single-repeat shortcut.
- **S2 — Loop a region instead of copying it** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple's Loop regions page documents the upper-right-corner drag gesture and L as the loop toggle; loop repetitions are re-plays of the same region, so editing the original does propagate.
- **S2 — Zoom all the way out and squint** *(cleared by the auditor, downgraded by the skeptic)*  
  Multiple independent Logic sources agree that Z is Toggle Zoom to fit Selection or All Contents and that with nothing selected it fits the whole project.
- **S3 — Z is the only zoom command you need** *(cleared by the auditor, downgraded by the skeptic)*  
  The command is literally named "Toggle Zoom to fit Selection or All Contents" and is on Z. Multiple independent Logic educators state both halves of the claim: Z zooms to the selection, Z again toggles back, and with nothing selected it fits all project content. professionalcomposers.com, masteringi
- **S3 — Know what the number keys actually do**  
  Half of this is solid: Apple's "Create and recall screensets" page confirms the top-row number keys recall screensets ("press any numeric key except 0"), and Apple's "Navigate using markers" page confirms the Go to Marker Number 1–20 commands exist and are assignable. But the load-bearing second cla
- **S3 — Assign a key to “Play Selection”**  
  No external source documents a Logic Pro command named "Play Selection", and nothing supports the claim that it is unassigned by default. What the sources do show are two differently named commands that both already have defaults: "Play/Stop Selection" (Control-Space, in the "Windows showing audio f
- **S3 — Jump to an exact bar with the Go to Position dialog** *(cleared by the auditor, downgraded by the skeptic)*  
  masteringinlogic.com states plainly that Go to Position is pre-assigned to the forward slash and that you type a bar (or SMPTE) position into it; Apple's "Set the playhead position" User Guide page documents the same Go to Position dialog for moving the playhead to an exact position. Two independent
- **S3 — Scroll horizontally without the scrollbar**  
  The trackpad half is supported — Apple's "Scroll and zoom in the Tracks area" page says gestures can be used to scroll the Tracks area, and Apple's trackpad page for Logic Pro states "Drag with two fingers to scroll areas horizontally and vertically". The Shift-plus-wheel half is not: the only suppo
- **S3 — Use the Cycle area as a bookmark**  
  The U part checks out: Apple's Global Commands table assigns U to "Set Rounded Locators by Regions/Events and Enable Cycle" (⌘U is the non-rounded version), so U does set the locators around your selection. But the actual payoff claim — that clicking the cycle bar in the ruler takes you straight bac
- **S4 — Record MIDI while the transport is stopped** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple confirms both halves: MIDI Flashback Capture works with the transport stopped, and it captures controller data as well as notes. Worth adding as a caveat (Apple states it, the book doesn't): after a 20-second gap between incoming MIDI events, the events before the pause are discarded — so 'alw
- **S4 — Transpose only the notes, permanently** *(cleared by the auditor, downgraded by the skeptic)*  
  Two independent Logic educators agree on both key commands as written: ⌥↑/⌥↓ for semitones and ⇧⌥↑/⇧⌥↓ for octaves, applied to selected MIDI events. The 'plain arrows move the selection' claim is supported for left/right (they select the adjacent note). Apple's own Piano Roll key-command table would
- **S4 — Double a part an octave down without a second track** *(cleared by the auditor, downgraded by the skeptic)*  
  Both mechanisms are externally supported: Transposer transposes incoming MIDI in real time, and Apple documents ⌥-drag as the way to copy notes in the Piano Roll. Velocity '-20' is taste, not a checkable claim. Editorial flag for the owner, not a factual error: the title promises 'without a second t
- **S4 — Record into a cycle with take folders** *(cleared by the auditor, downgraded by the skeptic)*  
  C for Cycle is confirmed by Apple, and Apple's Recording settings confirm the take-folder behaviour on MIDI cycle passes exactly as described.
- **S4 — Use Replace mode to punch over a bad bar** *(cleared by the auditor, downgraded by the skeptic)*  
  Replace is a control-bar button and it erases rather than layers, as written. Optional improvement for the owner: Apple documents the / key on the numeric keypad as the Replace toggle, and a Replace pop-up menu (click-and-hold the button) that selects exactly what gets erased — worth adding since th
- **S4 — Name the region before you move on** *(cleared by the auditor, downgraded by the skeptic)*  
  ⇧N as the rename-selected-regions command is confirmed by 9to5Mac's naming-regions piece, and Apple's Rename regions page covers the Text tool and inspector routes the trick also lists. The 'twenty untitled regions' line is advice, not a claim.
- **S4 — Use ⌘D to duplicate an instrument track with all its settings** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple documents Command-D as the default key command for New Track with Duplicate Setting, and current-era Logic shortcut references (Audeobox's 2026 cheat sheet, The Pro Audio Files) still list it that way, so the version trap is covered. One clarification worth adding: it creates a new EMPTY track
- **S4 — Drag a MIDI region onto an audio track to bounce it instantly**  
  I could find no source for dragging a MIDI region ONTO an existing audio track and having Logic bounce it. What Apple actually documents is a different gesture: dragging a region to the track header AREA (below the last header, or between two headers) creates a new track and bounces the region to an
- **S4 — Humanise deliberately with the Randomise function** *(cleared by the auditor, downgraded by the skeptic)*  
  The path is right: MIDI Transform is reached from the Functions menu at the top of the Piano Roll window, and the Humanize preset randomises position, velocity and note length, with 10 ticks as the stock randomisation amount — which is exactly the 5-to-10-tick range the trick recommends. Sound on So
- **S5 — Select similar notes with Edit > Select > Same Note Pitch**  
  No Apple page or reputable educator documents a menu item called "Same Note Pitch" under Edit > Select. Repeated searches surfaced only Edit > Select > Similar Events (⇧S) and the keyboard-click method. The exact menu path as written could not be confirmed anywhere, and the sub-claim that it "respec
- **S5 — Select all following notes** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple's "Select notes in the Piano Roll Editor" page documents this command in the Piano Roll's Edit > Select submenu, i.e. scoped to the notes being edited.
- **S5 — Rubber‑band select without hitting notes** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple's Piano Roll select-notes page lists dragging to enclose notes (marquee/rubber-band) and Shift as the extend-selection modifier.
- **S5 — Use Select > Inside Locators to grab a bar range**  
  Apple documents Select Inside Locators only for regions in the Tracks area ("to select all regions between the left and right locators"). No Apple page or reputable educator confirms it selecting NOTES inside the locators in the Piano Roll; the only support for that was an unattributed shortcut-list
- **S5 — Nudge notes by tick with ⌥ and the arrow keys** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple documents the Option-Arrow nudge-by-nudge-value workflow; macProVideo (reputable Logic educator) documents it specifically for notes in the Piano Roll with a tick-sized nudge value, and Pro Mix Academy confirms the Edit > Move > Set Nudge Value To menu path.
- **S5 — Type one length and every selected note follows**  
  Rests on the same unsourced "event inspector" mechanism as the previous trick — no external source confirms that typing a length applies to every selected note. The Force Legato contrast IS sourceable, so the trick is salvageable by dropping the inspector mechanism and naming the real menu command.
- **S5 — Draw a velocity ramp across a selection**  
  Nothing external supports drawing a velocity line across a lane with the Pointer or Pencil in the Piano Roll, and nothing supports ⌘ as the "keep relative differences" modifier. Apple documents relative-velocity behaviour as automatic when several notes are edited, and documents ⌥ (not ⌘) as the mod
- **S5 — Scale velocities rather than replacing them** *(cleared by the auditor, downgraded by the skeptic)*  
  Apple states the relative-difference behaviour when editing multiple notes' velocity, which is the trick's actionable claim. Caveat for the owner: the opening premise that typing a velocity value flattens everything to the same number is not separately sourced anywhere I could find, and if that sent
- **S5 — Show the automation lane inside the Piano Roll**  
  Apple documents opening the Piano Roll's Automation/MIDI area via a Show/Hide Automation button in the Piano Roll Editor menu bar, and says nothing about the A key doing it when the Piano Roll is focused. A is Logic's global Show/Hide Automation key command for the Tracks area; no source confirms it

## Survived both passes

Confirmed against Apple's guide or two independent references, and sustained under challenge.

- **S1 — Run two buffer sizes, not one** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/configure-a-connected-audio-device-lgcpebe7fb26/mac
- **S1 — Set Processing Threads to Automatic** · `VERIFIED`  
  https://support.apple.com/en-us/101921
- **S1 — Raise Process Buffer Range to Large for mixing** · `VERIFIED`  
  https://support.apple.com/en-us/108295
- **S1 — Uncheck Software Monitoring if you monitor through your interface** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/general-audio-preferences-lgcp0ed343a9/mac
- **S1 — Turn on scrubbing with audio in the Tracks area** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/audio-editing-preferences-lgcp0d6a4f6f/mac
- **S1 — Fix doubled notes from a controller** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/general-project-settings-lgcp94b70f34/mac
- **S1 — Turn on Enable Complete Features first, always** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/advanced-settings-lgcpb6dcc6fa/mac
- **S1 — Turn on “Show Help Tags”** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/general-settings-lgcp9793a910/mac
- **S1 — Turn on “Select regions on track selection”** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/select-regions-lgcpf7c0e62a/10.7/mac/11.0
- **S1 — Read the Clean Up list before you confirm it** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/clean-up-projects-lgcpce0efc05/mac
- **S1 — Turn on Smart Tempo “Keep Project Tempo” by default** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/choose-the-project-tempo-mode-lgcpca199cf6/mac
- **S1 — Stop new recordings arriving pre-quantised** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/use-the-region-inspector-lgcpd8a8780c/mac
- **S1 — Set Tuning to Equal Temperament unless you mean otherwise** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/tuning-project-settings-lgcp452f2693/mac
- **S1 — Save a Session Start template and set it as the default** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/project-handling-settings-lgcp43defb63/mac
- **S1 — Move the Sound Library to an external drive on purpose** · `VERIFIED`  
  https://support.apple.com/en-us/111094
- **S2 — Use the Arrangement track to move whole sections** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/edit-arrangement-markers-lgcpf7c0a3d7/mac
- **S2 — ⌥‑drag an arrangement marker to duplicate a section** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/edit-arrangement-markers-lgcpf7c0a3d7/mac
- **S2 — Delete a section and close the gap** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/edit-arrangement-markers-lgcpf7c0a3d7/mac
- **S2 — Use aliases for parts that must stay identical** · `VERIFIED`  
  https://support.apple.com/en-lb/guide/logicpro/lgcpf7c0cea3/10.7/mac/11.0
- **S2 — Make a folder out of a section** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/pack-and-unpack-folders-lgcpf7c0cb8e/mac
- **S2 — Colour‑code sections, not instruments** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/change-the-color-of-regions-lgcpf7c0db8c/mac
- **S2 — Use Track Stacks to collapse instrument families** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/create-and-edit-track-stacks-lgcp5bafa811/10.7/mac/11.0
- **S2 — Keep a “graveyard” track at the bottom** · `NO_FACTUAL_CLAIM`
- **S2 — Use markers for notes to self, not just sections** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/rename-markers-lgcp4d438ec1/mac
- **S3 — Drag‑zoom to any area with ⌃⌥** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/zoom-windows-lgcp5cbf2096/mac
- **S4 — Use the Step Input Keyboard for parts you cannot play** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/use-step-input-recording-techniques-lgcpb19a8406/mac
- **S4 — Transpose without touching the notes** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/midi-region-parameters-lgcpf7c0d270/10.7/mac/11.0
- **S4 — Merge takes when you are layering, not replacing** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/recording-preferences-lgcp411dd5c8/mac
- **S4 — Freeze the instrument as soon as the part is done** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/freeze-tracks-lgcpf1cbfd51/10.7/mac/11.6
- **S4 — Keep one “sketch” instrument track loaded at all times** · `NO_FACTUAL_CLAIM`
- **S5 — Select all notes of the same pitch in one click** · `VERIFIED`  
  https://support.apple.com/en-mn/guide/logicpro/lgcpa906bc30/10.7/mac/11.0
- **S5 — Colour notes by velocity to read dynamics instantly** · `VERIFIED`  
  https://support.apple.com/en-eg/guide/logicpro/lgcpa8fbe9d9/10.7/mac/11.0
- **S5 — Quantise from the region inspector, not destructively** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/quantize-parameter-values-lgcp47452db8/mac
- **S5 — Use Q‑Strength to keep the human feel** · `VERIFIED`  
  https://support.apple.com/guide/logicpro/advanced-quantization-parameters-lgcp35029a2b/mac
- **S5 — Quantise only the notes that need it** · `VERIFIED`  
  https://support.apple.com/en-mo/guide/logicpro/quantize-the-timing-of-notes-lgcpfa6e7f80/10.7/mac/11.0
