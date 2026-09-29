#!/usr/bin/env python3
"""Merge the cite-and-verify workflow results into content/.

Each trick in the book was re-checked by a verifier that had to cite a source
for every claim, then by a skeptic whose job was to trim any sentence the
cited source does not support. This applies the outcome:

    verifier KEEP / FIX   -> the verified text, with its sources attached
    verifier ADVICE       -> kept, marked "advice" (no factual claim to cite)
    skeptic  TRIM         -> body cut back to what the sources support
    verifier or skeptic CUT, or KEEP/FIX with no source -> removed

A trick the results never reached is left untouched and reported loudly —
coverage gaps must not silently delete content.

    python3 apply_citations.py audit/cite-*.json            # report only
    python3 apply_citations.py audit/cite-*.json --apply    # write content/ + CITED.md
"""
import argparse, collections, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
CONTENT = HERE / "content"


def load(paths):
    """{section: {index: decision}} from one or more workflow result files."""
    out = collections.defaultdict(dict)
    dead = []
    for p in paths:
        data = json.loads(pathlib.Path(p).read_text())
        for r in data.get("results", []):
            u, v = r.get("unit") or {}, r.get("verify")
            if not v or v.get("search_worked") is False:
                dead.append(u.get("id")); continue
            ch = {c["index"]: c for c in ((r.get("challenge") or {}).get("reviews") or [])}
            for t in v.get("tricks", []):
                i = t["index"]
                if not (u["start"] <= i < u["end"]):
                    continue                      # stray index outside the slice
                d = dict(t)
                c = ch.get(i)
                if c and c["outcome"] == "CUT":
                    d["action"], d["reason"] = "CUT", f"{t.get('reason','')} — SKEPTIC: {c['reason']}"
                elif c and c["outcome"] == "TRIM":
                    d["final_body"] = c.get("trimmed_body") or d.get("final_body")
                    d["final_key"] = c.get("trimmed_key", "")
                    d["trimmed"] = c["reason"]
                out[u["section"]][i] = d
    return out, dead


def clean_sources(srcs):
    seen, keep = set(), []
    for s in srcs or []:
        url = (s.get("url") or "").strip()
        if not url.startswith("https://") or url in seen:
            continue
        seen.add(url)
        keep.append({"label": (s.get("label") or url).strip(), "url": url})
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    decisions, dead = load(a.results)
    log = collections.defaultdict(list)
    counts = collections.Counter()
    untouched = []

    for path in sorted(CONTENT.glob("[0-9][0-9].json")):
        sec = json.loads(path.read_text()); n = sec["number"]
        table = decisions.get(n, {})
        idx = 0
        for g in sec["groups"]:
            kept = []
            for tip in g["tips"]:
                d = table.get(idx); idx += 1
                if d is None:
                    untouched.append((n, tip["t"])); kept.append(tip); counts["untouched"] += 1
                    continue
                act = d["action"]
                srcs = clean_sources(d.get("sources"))
                if act in ("KEEP", "FIX") and not srcs:
                    act = "CUT"; d["reason"] = "no usable source returned — " + d.get("reason", "")
                if act == "CUT":
                    counts["cut"] += 1
                    log["cut"].append((n, tip["t"], d.get("reason", "")))
                    continue
                new = dict(tip)
                new["t"] = (d.get("final_title") or tip["t"]).strip()
                new["d"] = (d.get("final_body") or tip["d"]).strip()
                k = (d.get("final_key") or "").strip()
                if k: new["k"] = k
                else: new.pop("k", None)
                if act == "ADVICE":
                    new["advice"] = True
                    if srcs: new["src"] = srcs
                    else: new.pop("src", None)
                else:
                    new.pop("advice", None)
                    new["src"] = srcs
                changed = (new["t"], new["d"], new.get("k")) != (tip["t"], tip["d"], tip.get("k"))
                key = "trimmed" if d.get("trimmed") else ("fixed" if changed else act.lower())
                counts[key] += 1
                if changed:
                    log[key].append((n, tip["t"], new, d.get("trimmed") or d.get("reason", "")))
                kept.append(new)
            g["tips"] = kept
        sec["groups"] = [g for g in sec["groups"] if g["tips"]]
        if a.apply:
            path.write_text(json.dumps(sec, ensure_ascii=False, indent=2) + "\n")

    total = sum(counts.values()) - counts["cut"]
    print("  ".join(f"{k}={v}" for k, v in sorted(counts.items())), f"| survives {total}")
    if dead: print("UNITS WITH DEAD SEARCH (not applied):", dead)
    if untouched:
        print(f"\n{len(untouched)} tricks never reached by the results — left as they were:")
        for n, t in untouched[:30]: print(f"  S{n}  {t}")
    if not a.apply:
        print("\n(report only — pass --apply to write)"); return

    doc = ["# Citation pass — what changed", "",
           "Every trick was re-checked against a cited source, then challenged by a second",
           "agent whose job was to strip any sentence the source does not support.", "",
           "**" + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())) + f" · survives {total}**", ""]
    for title, key in (("Corrected", "fixed"), ("Trimmed to what the source supports", "trimmed")):
        doc += [f"## {title} ({len(log[key])})", ""]
        for n, old, new, why in log[key]:
            src = " · ".join(f"[{s['label']}]({s['url']})" for s in new.get("src", []))
            doc.append(f"- **S{n} — {old}**" + (f" → *{new['t']}*" if new["t"] != old else "")
                       + f"  \n  {new['d']}" + (f"  \n  Key: `{new['k']}`" if new.get("k") else "")
                       + f"  \n  Why: {why}" + (f"  \n  Source: {src}" if src else ""))
        doc.append("")
    doc += [f"## Removed ({len(log['cut'])})", ""]
    doc += [f"- **S{n} — {t}**  \n  {why}" for n, t, why in log["cut"]]
    (HERE / "CITED.md").write_text("\n".join(doc) + "\n")
    print("\nwrote CITED.md")


if __name__ == "__main__":
    main()
