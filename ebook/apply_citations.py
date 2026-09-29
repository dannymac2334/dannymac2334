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


def load_overrides(path):
    """Rescue / modernize / front-matter results from the follow-up workflow.

    Trick decisions override the batch decision for the same (section, index);
    a skeptic TRIM or CUT is folded in first. Front-matter decisions are keyed
    by item id ("basics:<table>:<row>", "legend:<symbol>", "legend:callout").
    """
    tricks, front = {}, {}
    for r in json.loads(pathlib.Path(path).read_text()):
        v = r.get("verify")
        if not v or v.get("search_worked") is False:
            continue
        ch = {c["ref"]: c for c in ((r.get("challenge") or {}).get("reviews") or [])}
        if r["kind"] == "front":
            for it in v.get("items", []):
                d = dict(it); c = ch.get(it["id"])
                if c and c["outcome"] == "CUT":
                    d["action"] = "CUT"
                elif c and c["outcome"] == "TRIM":
                    d["final_text"] = c.get("trimmed_text") or d.get("final_text")
                    if "trimmed_key" in c and c["trimmed_key"]:
                        d["final_key"] = c["trimmed_key"]
                front[it["id"]] = d
        else:
            for t in v.get("tricks", []):
                d = dict(t); c = ch.get(f"S{t['section']}#{t['index']}")
                if c and c["outcome"] == "CUT":
                    d["action"], d["reason"] = "CUT", f"{t.get('reason','')} — SKEPTIC: {c['reason']}"
                elif c and c["outcome"] == "TRIM":
                    d["final_body"] = c.get("trimmed_text") or d.get("final_body")
                    d["final_key"] = c.get("trimmed_key", "")
                    d["trimmed"] = c["reason"]
                d["override"] = r["kind"]
                tricks[(t["section"], t["index"])] = d
    return tricks, front


def apply_front(front_dec, sources_of):
    """Rewrite 00-front.json's key tables, legend and callout from verdicts."""
    f = CONTENT / "00-front.json"; d = json.loads(f.read_text()); changes = []
    for page in d["pages"]:
        if page["id"] == "basics":
            for tbl in page["tables"]:
                rows, srcs = [], []
                for i, (key, text) in enumerate(tbl["rows"]):
                    dec = front_dec.get(f"basics:{tbl['heading']}:{i}")
                    if dec is None:
                        rows.append([key, text]); changes.append(("UNJUDGED", key, text)); continue
                    if dec["action"] == "CUT":
                        changes.append(("CUT", key, text + " — " + dec.get("reason", ""))); continue
                    nk, nt = (dec.get("final_key") or key).strip(), (dec.get("final_text") or text).strip()
                    if (nk, nt) != (key, text): changes.append(("FIX", f"{key} → {nk}", f"{text} → {nt}"))
                    rows.append([nk, nt]); srcs += sources_of(dec)
                tbl["rows"] = rows
                tbl["src"] = clean_sources(srcs)
            page["tables"] = [t for t in page["tables"] if t["rows"]]
        if page["id"] == "legend":
            keys, srcs = [], []
            for k in page["keys"]:
                dec = front_dec.get(f"legend:{k['sym']}")
                if dec is None:
                    keys.append(k); changes.append(("UNJUDGED", k["sym"], k["note"])); continue
                if dec["action"] == "CUT":
                    changes.append(("CUT", k["sym"], k["note"])); continue
                nt = (dec.get("final_text") or k["note"]).strip()
                if nt != k["note"]: changes.append(("FIX", k["sym"], f"{k['note']} → {nt}"))
                keys.append({**k, "note": nt}); srcs += sources_of(dec)
            page["keys"] = keys; page["keys_src"] = clean_sources(srcs)
            dec = front_dec.get("legend:callout")
            if dec is not None:
                if dec["action"] == "CUT":
                    changes.append(("CUT", "callout", page["callout"]["text"])); page.pop("callout", None)
                else:
                    nt = (dec.get("final_text") or page["callout"]["text"]).strip()
                    if nt != page["callout"]["text"]: changes.append(("FIX", "callout", nt))
                    page["callout"]["text"] = nt
                    page["callout"]["src"] = clean_sources(sources_of(dec))
    return d, changes


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
    ap.add_argument("--overrides", help="rescue/modernize/front-matter results (applied last)")
    a = ap.parse_args()

    decisions, dead = load(a.results)
    front_dec = {}
    if a.overrides:
        otricks, front_dec = load_overrides(a.overrides)
        for (n, i), d in otricks.items():
            decisions[n][i] = d
        print(f"overrides: {len(otricks)} tricks, {len(front_dec)} front-matter items")
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

    front_changes = []
    if front_dec:
        fd, front_changes = apply_front(front_dec, lambda dec: dec.get("sources") or [])
        if a.apply:
            (CONTENT / "00-front.json").write_text(json.dumps(fd, ensure_ascii=False, indent=2) + "\n")
        fc = collections.Counter(c[0] for c in front_changes)
        print("front matter:", dict(fc) or "all kept as written")

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
    if front_changes:
        doc += ["", f"## Front matter — key tables, legend, callout ({len(front_changes)} changes)", ""]
        doc += [f"- `{kind}` {a_} — {b_}" for kind, a_, b_ in front_changes]
    (HERE / "CITED.md").write_text("\n".join(doc) + "\n")
    print("\nwrote CITED.md")


if __name__ == "__main__":
    main()
