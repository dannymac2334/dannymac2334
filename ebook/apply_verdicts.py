#!/usr/bin/env python3
"""Apply an audit verdict file to content/, and write down what it removed.

The audit (workflows/verify-logic-book) returns one verdict per trick. This turns
those verdicts into edits:

    VERIFIED          keep as written
    NO_FACTUAL_CLAIM  keep as written — advice, nothing a buyer can call inaccurate
    WRONG             rewrite if the audit supplied an externally-sourced correction,
                      otherwise remove
    UNVERIFIABLE      rewrite to the audit's `salvage` copy if it offered one,
                      otherwise remove

Nothing is deleted silently. Every removal and every rewrite lands in REMOVED.md
with the reason and the evidence, so the cut is reviewable after the fact and
reversible from git.

    python3 apply_verdicts.py verdicts.json            # report only, no writes
    python3 apply_verdicts.py verdicts.json --apply    # actually edit content/
"""

import argparse
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
CONTENT = HERE / "content"

KEEP = {"VERIFIED", "NO_FACTUAL_CLAIM"}


def load_verdicts(path):
    """Flatten the workflow's nested result into {section: {title: verdict}}.

    The skeptic pass runs after the audit, so its downgrades win.
    """
    raw = json.loads(pathlib.Path(path).read_text())
    out = collections.defaultdict(dict)
    for entry in raw.get("sections", []):
        audit = entry.get("audit")
        if not audit:
            continue
        n = audit.get("section", entry.get("section"))
        downgrades = {
            d["title"]: d
            for d in ((entry.get("challenge") or {}).get("downgrades") or [])
        }
        for tip in audit.get("tricks", []):
            v = dict(tip)
            hit = downgrades.get(tip["title"])
            if hit:
                v["verdict"] = hit["new_verdict"]
                v["reason"] = f"{tip.get('reason', '')} — SKEPTIC: {hit['reason']}"
                v["downgraded"] = True
                # a downgraded trick cannot lean on the auditor's correction,
                # which the skeptic has just rejected
                v.pop("correction", None)
            out[n][tip["title"]] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verdicts")
    ap.add_argument("--apply", action="store_true", help="write the changes")
    args = ap.parse_args()

    verdicts = load_verdicts(args.verdicts)
    if not verdicts:
        sys.exit("no verdicts found in that file")

    removed, rewritten, kept, unjudged = [], [], 0, []

    for path in sorted(CONTENT.glob("[0-9][0-9].json")):
        sec = json.loads(path.read_text())
        n = sec["number"]
        table = verdicts.get(n, {})
        touched = False

        for group in sec["groups"]:
            surviving = []
            for tip in group["tips"]:
                v = table.get(tip["t"])

                if v is None:
                    # no verdict reached this trick — treat as unproven, but say so
                    # loudly rather than deleting on the strength of a gap
                    unjudged.append((n, tip["t"]))
                    surviving.append(tip)
                    continue

                verdict = v["verdict"]

                if verdict in KEEP:
                    kept += 1
                    surviving.append(tip)
                    continue

                replacement = (
                    v.get("correction") if verdict == "WRONG" else v.get("salvage")
                )
                if replacement and replacement.strip():
                    rewritten.append((n, tip["t"], verdict, v.get("reason", ""), replacement))
                    tip["d"] = replacement.strip()
                    if verdict == "UNVERIFIABLE" and tip.get("k"):
                        # the key command is usually the unprovable part
                        tip.pop("k")
                    touched = True
                    surviving.append(tip)
                else:
                    removed.append(
                        (n, tip["t"], verdict, v.get("reason", ""), v.get("evidence_url", ""))
                    )
                    touched = True

            group["tips"] = surviving

        sec["groups"] = [g for g in sec["groups"] if g["tips"]]

        if touched and args.apply:
            path.write_text(json.dumps(sec, ensure_ascii=False, indent=2) + "\n")

    total = kept + len(rewritten) + len(removed) + len(unjudged)
    print(f"judged {total} tricks")
    print(f"  kept as written   {kept}")
    print(f"  rewritten         {len(rewritten)}")
    print(f"  REMOVED           {len(removed)}")
    print(f"  no verdict        {len(unjudged)}")
    print(f"\nsurvives: {kept + len(rewritten) + len(unjudged)}")

    if unjudged:
        print("\nNo verdict reached these — kept, but unproven:")
        for n, t in unjudged[:40]:
            print(f"  S{n}  {t}")
        if len(unjudged) > 40:
            print(f"  … and {len(unjudged) - 40} more")

    if not args.apply:
        print("\n(report only — pass --apply to write)")
        return

    doc = [
        "# What was cut, and why",
        "",
        "Every trick removed or rewritten in the verification pass, with the reason.",
        "Nothing here was deleted on a hunch: each one either failed against an external",
        "source or could not be confirmed by one. The full text is recoverable from git",
        "history if any of these turn out to be defensible.",
        "",
        f"**Removed {len(removed)} · rewritten {len(rewritten)} · kept {kept}**",
        "",
        "## Removed",
        "",
    ]
    for n, title, verdict, reason, url in removed:
        doc.append(f"- **S{n} — {title}** · `{verdict}`  \n  {reason}"
                   + (f"  \n  {url}" if url else ""))
    doc += ["", "## Rewritten to something provable", ""]
    for n, title, verdict, reason, new in rewritten:
        doc.append(f"- **S{n} — {title}** · was `{verdict}`  \n  {reason}  \n  → {new}")
    if unjudged:
        doc += ["", "## Kept but never judged", "",
                "The audit did not return a verdict for these. They are still in the book.", ""]
        doc += [f"- S{n} — {t}" for n, t in unjudged]

    (HERE / "REMOVED.md").write_text("\n".join(doc) + "\n")
    print("\nwrote REMOVED.md")


if __name__ == "__main__":
    main()
