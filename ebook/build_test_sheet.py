#!/usr/bin/env python3
"""Build the hands-on Logic test run: every claim in the book, as a checklist.

Output: dist/test-sheet/logic-test-run.html (git-ignored), published as a private
Artifact. Each result is saved to the artifact's database (collection `results`,
one document per item: t-001 … t-248 for tricks, s-01 … for Start Here steps,
k-01 … for key-table rows), so Claude can read the failures back and fix them.

Regenerate after content changes; item ids are stable as long as trick order is.
"""

import json
import pathlib

from build import load, count_tips, keycap

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "dist" / "test-sheet" / "logic-test-run.html"


def items():
    front, sections = load()
    out = []
    for p in front["pages"]:
        for n, st in enumerate(p.get("steps", []), 1):
            out.append({"id": f"s-{n:02d}", "sec": "Start Here", "grp": "First steps", "t": st["title"],
                        "d": st["body"], "k": st.get("key") or "", "src": (st.get("src") or [{}])[0]})
    k = 0
    for p in front["pages"]:
        for tb in p.get("tables", []):
            for row in tb["rows"]:
                k += 1
                out.append({"id": f"k-{k:02d}", "sec": "Basic key commands", "grp": tb["heading"], "t": row[1],
                            "d": f"Press {row[0]}: {row[1]}.", "k": row[0],
                            "src": (row[2] if len(row) > 2 and row[2] else [{}])[0]})
    i = 0
    for s in sections:
        for g in s["groups"]:
            for t in g["tips"]:
                i += 1
                out.append({"id": f"t-{i:03d}", "sec": f"{s['number']:02d} {s['title']}", "grp": g["heading"],
                            "t": t["t"], "d": t["d"], "k": t.get("k") or "",
                            "src": (t.get("src") or [{}])[0], "n": i})
    return out, count_tips(sections)


PAGE = r"""<title>Logic Test Run</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap">
<style>
/* Layout: one working column — setup and progress on top, a sticky filter bar,
   then the book's own order, section by section. Deliberately one light theme,
   the rates-page paper and ink, with no grey text anywhere. */
:root{
  --paper:#fdfdfd; --ink:#0a0a0a; --line:rgba(0,0,0,.16); --line-strong:rgba(0,0,0,.45);
  --pass:#0e7a3e; --fail:#c0261e; --fix:#f2b705; --on:#ffffff;
  --font:"Figtree","Helvetica Neue",Helvetica,Arial,sans-serif;
  color-scheme:light;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
::placeholder{color:var(--ink);opacity:1;font-style:italic}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.5}
.wrap{max-width:980px;margin:0 auto;padding-inline:16px;padding-block:32px 80px}
h1{margin:0;font-size:clamp(34px,6vw,56px);line-height:.98;letter-spacing:-.045em;text-wrap:balance}
.kicker{margin:0 0 14px;font-size:12px;font-weight:600;letter-spacing:.22em;text-transform:uppercase}
.lede{margin:16px 0 0;max-width:62ch;font-size:17px}
.panel{margin-top:28px;border:1px solid var(--line);border-radius:16px;padding:20px}
.how{margin-top:16px}
.how summary{cursor:pointer;font-weight:700}
.how ol{margin:12px 0 0;padding-left:20px;display:grid;gap:6px}
.setup{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}
label{display:grid;gap:6px;font-size:13px;font-weight:600}
input,select,textarea{font:inherit;color:var(--ink);background:#fff;border:1px solid var(--line-strong);border-radius:10px;padding:10px 12px;min-width:0}
input:focus,select:focus,textarea:focus{outline:2px solid var(--ink);outline-offset:1px}
.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:20px}
.stat{border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.stat b{display:block;font-size:26px;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stat span{font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase}
.bar{margin-top:14px;height:10px;border-radius:99px;background:rgba(0,0,0,.08);overflow:hidden;display:flex}
.bar i{display:block;height:100%}
.tools{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--paper);border-bottom:1px solid var(--line);
  margin-top:24px;padding-block:12px;display:grid;grid-template-columns:2fr 1.4fr 1fr;gap:10px}
.notice{margin-top:16px;border:2px solid var(--ink);border-radius:12px;padding:12px 14px;font-weight:600}
.sec{margin-top:36px}
.sec h2{margin:0 0 4px;font-size:24px;letter-spacing:-.03em}
.grp{margin:18px 0 8px;font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;padding-bottom:8px;border-bottom:1px solid var(--line)}
.item{border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-top:10px;display:grid;gap:10px}
.item[data-s="pass"]{border-color:var(--pass)}
.item[data-s="fail"]{border-color:var(--fail);border-width:2px}
.item[data-s="fix"]{border-color:#b98900;border-width:2px}
.top{display:flex;gap:10px;align-items:baseline;justify-content:space-between;flex-wrap:wrap}
.id{font-size:12px;font-weight:600;letter-spacing:.16em;font-variant-numeric:tabular-nums}
.chip{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;border-radius:99px;padding:4px 10px;border:1px solid var(--ink)}
.chip.pass{background:var(--pass);border-color:var(--pass);color:var(--on)}
.chip.fail{background:var(--fail);border-color:var(--fail);color:var(--on)}
.chip.fix{background:var(--fix);border-color:var(--fix);color:var(--ink)}
.item h3{margin:0;font-size:18px;letter-spacing:-.02em;line-height:1.25;min-width:0}
.item p{margin:0;max-width:70ch}
.keys{display:flex;gap:6px;flex-wrap:wrap}
.kbd{display:inline-block;font-weight:600;font-size:12px;letter-spacing:.08em;text-transform:uppercase;background:var(--ink);color:var(--on);border-radius:99px;padding:5px 12px}
.kbd-phrase{background:transparent;color:var(--ink);border:1px solid var(--ink)}
.src{font-size:13px}
.src a{color:var(--ink);text-underline-offset:2px}
.acts{display:flex;gap:8px;flex-wrap:wrap}
.acts button{font:inherit;font-size:14px;font-weight:600;cursor:pointer;border-radius:99px;padding:9px 16px;border:1px solid var(--ink);background:#fff;color:var(--ink)}
.acts button:hover{background:rgba(0,0,0,.05)}
.acts button:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.acts button[aria-pressed="true"].b-pass{background:var(--pass);border-color:var(--pass);color:var(--on)}
.acts button[aria-pressed="true"].b-fail{background:var(--fail);border-color:var(--fail);color:var(--on)}
.acts button[aria-pressed="true"].b-fix{background:var(--fix);border-color:var(--fix);color:var(--ink)}
.acts button[aria-pressed="true"].b-skip{background:var(--ink);color:var(--on)}
.acts button:disabled{cursor:not-allowed;opacity:.5}
textarea{width:100%;min-height:64px;resize:vertical}
.saved{font-size:12px;font-weight:600}
.empty{margin-top:30px;font-weight:600}
@media (max-width:640px){
  .stats{grid-template-columns:repeat(3,minmax(0,1fr))}
  .tools{grid-template-columns:1fr 1fr}
  .tools input{grid-column:1/-1}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">
  <p class="kicker">Logic Pro Crash Course · hands-on check</p>
  <h1>Logic Test Run</h1>
  <p class="lede">Every claim in the book, one by one. Try each in Logic and mark what happened.
    Your results save as you go, and Claude reads the failures back to fix the book.</p>

  <section class="panel" aria-labelledby="setup-h">
    <h2 id="setup-h" style="margin:0;font-size:18px;letter-spacing:-.02em">Your setup</h2>
    <div class="setup">
      <label for="f-logic">Logic Pro version <input id="f-logic" placeholder="e.g. 12.0.1" autocomplete="off"></label>
      <label for="f-macos">macOS version <input id="f-macos" placeholder="e.g. macOS 26.0" autocomplete="off"></label>
      <label for="f-kb">Keyboard layout <input id="f-kb" placeholder="e.g. US" autocomplete="off"></label>
    </div>
    <details class="how">
      <summary>How to test</summary>
      <ol>
        <li>Use a new, empty project and the default key commands (Logic Pro › Key Commands › Presets › US).</li>
        <li>Do exactly what the item says. Don't use outside knowledge to fill a gap.</li>
        <li><b>Works</b>: it did what the text says, with the keys shown.</li>
        <li><b>Wording fix</b>: it works, but a name, menu path or detail in the text is off. Say what.</li>
        <li><b>Doesn't work</b>: it didn't happen, or something else did. Say what you saw.</li>
        <li><b>Can't test</b>: needs hardware or a setup you don't have. It stays open for later.</li>
      </ol>
    </details>
    <div class="stats" id="stats"></div>
    <div class="bar" id="bar" aria-hidden="true"></div>
  </section>

  <div class="notice" id="offline" hidden>Saving is off in this view, so results won't be kept. Open the page from your own Claude account to save.</div>

  <div class="tools" role="search">
    <input id="f-q" type="search" placeholder="Find an item" aria-label="Find an item" autocomplete="off">
    <select id="f-sec" aria-label="Section"></select>
    <select id="f-st" aria-label="Status">
      <option value="">All statuses</option>
      <option value="open">Not tested yet</option>
      <option value="fail">Doesn't work</option>
      <option value="fix">Wording fix</option>
      <option value="pass">Works</option>
      <option value="skip">Can't test</option>
    </select>
  </div>

  <main id="list"></main>
  <p class="empty" id="none" hidden>Nothing matches those filters.</p>
</div>

<script type="application/json" id="data">__DATA__</script>
<script>
(function () {
  var ITEMS = JSON.parse(document.getElementById('data').textContent);
  var LABEL = {pass: 'Works', fix: 'Wording fix', fail: "Doesn't work", skip: "Can't test"};
  var results = {};           // id -> {status, note}
  var els = {};               // id -> element refs
  var db = null;
  var listEl = document.getElementById('list');

  /* ---------- render once, then update in place ---------- */
  var secSel = document.getElementById('f-sec');
  var secs = [];
  ITEMS.forEach(function (it) { if (secs.indexOf(it.sec) === -1) secs.push(it.sec); });
  secSel.innerHTML = '<option value="">All sections</option>' + secs.map(function (s) {
    return '<option>' + esc(s) + '</option>'; }).join('');

  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  var lastSec = null, lastGrp = null, secEl = null;
  ITEMS.forEach(function (it) {
    if (it.sec !== lastSec) {
      secEl = document.createElement('section'); secEl.className = 'sec'; secEl.dataset.sec = it.sec;
      secEl.innerHTML = '<h2>' + esc(it.sec) + '</h2>';
      listEl.appendChild(secEl); lastSec = it.sec; lastGrp = null;
    }
    if (it.grp !== lastGrp) {
      var g = document.createElement('p'); g.className = 'grp'; g.textContent = it.grp; g.dataset.grp = it.sec + '|' + it.grp;
      secEl.appendChild(g); lastGrp = it.grp;
    }
    var a = document.createElement('article'); a.className = 'item'; a.id = it.id; a.dataset.s = 'open';
    a.dataset.grp = it.sec + '|' + it.grp;
    var src = it.src && it.src.url ? '<p class="src">Check against: <a href="' + esc(it.src.url) + '" target="_blank" rel="noopener">' + esc(it.src.label) + '</a></p>' : '';
    a.innerHTML =
      '<div class="top"><span class="id">' + esc(it.id.toUpperCase()) + '</span><span class="chip" hidden></span></div>' +
      '<h3>' + esc(it.t) + '</h3><p>' + esc(it.d) + '</p>' +
      (it.kh ? '<div class="keys">' + it.kh + '</div>' : '') + src +
      '<div class="acts" role="group" aria-label="Result for ' + esc(it.t) + '">' +
        ['pass', 'fix', 'fail', 'skip'].map(function (s) {
          return '<button type="button" class="b-' + s + '" data-v="' + s + '" aria-pressed="false">' + LABEL[s] + '</button>'; }).join('') +
      '</div>' +
      '<label for="n-' + it.id + '" hidden>What happened<textarea id="n-' + it.id + '" placeholder="What did you see? What should the text say?"></textarea></label>' +
      '<span class="saved" aria-live="polite"></span>';
    secEl.appendChild(a);
    els[it.id] = {a: a, chip: a.querySelector('.chip'), btns: a.querySelectorAll('.acts button'),
                  noteWrap: a.querySelector('label'), note: a.querySelector('textarea'), saved: a.querySelector('.saved')};
    it._hay = (it.id + ' ' + it.t + ' ' + it.d + ' ' + it.k + ' ' + it.grp).toLowerCase();
  });

  function paint(id) {
    var r = results[id] || {}, e = els[id], s = r.status || 'open';
    e.a.dataset.s = s;
    e.chip.hidden = s === 'open';
    e.chip.className = 'chip ' + s; e.chip.textContent = LABEL[s] || '';
    e.btns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.v === s ? 'true' : 'false'); });
    var needNote = s === 'fail' || s === 'fix';
    e.noteWrap.hidden = !needNote && !r.note;
    if (document.activeElement !== e.note) e.note.value = r.note || '';
  }

  function stats() {
    var c = {pass: 0, fix: 0, fail: 0, skip: 0};
    Object.keys(results).forEach(function (id) { var s = results[id].status; if (c[s] !== undefined) c[s]++; });
    var done = c.pass + c.fix + c.fail + c.skip, total = ITEMS.length;
    document.getElementById('stats').innerHTML = [
      ['Tested', done + '/' + total], ['Works', c.pass], ['Wording fix', c.fix], ["Doesn't work", c.fail], ["Can't test", c.skip]
    ].map(function (x) { return '<div class="stat"><b>' + x[1] + '</b><span>' + x[0] + '</span></div>'; }).join('');
    var seg = function (n, col) { return n ? '<i style="width:' + (100 * n / total) + '%;background:' + col + '"></i>' : ''; };
    document.getElementById('bar').innerHTML = seg(c.pass, 'var(--pass)') + seg(c.fix, 'var(--fix)') +
      seg(c.fail, 'var(--fail)') + seg(c.skip, 'var(--ink)');
  }

  /* ---------- filters ---------- */
  var q = document.getElementById('f-q'), st = document.getElementById('f-st');
  function filter() {
    var words = q.value.toLowerCase().split(/\s+/).filter(Boolean), sec = secSel.value, want = st.value, any = false;
    var shownGrp = {}, shownSec = {};
    ITEMS.forEach(function (it) {
      var s = (results[it.id] || {}).status || 'open';
      var ok = (!sec || it.sec === sec) && (!want || s === want) &&
               words.every(function (w) { return it._hay.indexOf(w) !== -1; });
      els[it.id].a.hidden = !ok;
      if (ok) { any = true; shownGrp[it.sec + '|' + it.grp] = 1; shownSec[it.sec] = 1; }
    });
    listEl.querySelectorAll('.grp').forEach(function (g) { g.hidden = !shownGrp[g.dataset.grp]; });
    listEl.querySelectorAll('.sec').forEach(function (s) { s.hidden = !shownSec[s.dataset.sec]; });
    document.getElementById('none').hidden = any;
  }
  [q, secSel, st].forEach(function (x) { x.addEventListener('input', filter); });

  /* ---------- saving: one write at a time per document ---------- */
  var queue = {};
  function save(id, body, e) {
    if (!db) return;
    var run = function () {
      e && (e.saved.textContent = 'Saving…');
      return db.collection('results').doc(id).set(body).then(function () {
        e && (e.saved.textContent = 'Saved');
      }, function (err) {
        e && (e.saved.textContent = "Couldn't save (" + (err && err.code || 'error') + '). Try again.');
      });
    };
    queue[id] = (queue[id] || Promise.resolve()).then(run, run);
  }
  function record(id, patch) {
    var r = Object.assign({}, results[id] || {}, patch, {at: new Date().toISOString()});
    var meta = window.__meta || {};
    if (meta.logic) r.logic = meta.logic;
    results[id] = r; paint(id); stats();
    save(id, r, els[id]);
  }
  listEl.addEventListener('click', function (ev) {
    var b = ev.target.closest('.acts button'); if (!b) return;
    var id = b.closest('.item').id;
    var cur = (results[id] || {}).status;
    record(id, {status: cur === b.dataset.v ? 'open' : b.dataset.v});
    if ((b.dataset.v === 'fail' || b.dataset.v === 'fix') && cur !== b.dataset.v) els[id].note.focus();
  });
  var noteTimers = {};
  listEl.addEventListener('input', function (ev) {
    if (ev.target.tagName !== 'TEXTAREA') return;
    var id = ev.target.closest('.item').id, v = ev.target.value;
    clearTimeout(noteTimers[id]);
    noteTimers[id] = setTimeout(function () { record(id, {note: v}); }, 700);
  });

  /* setup fields -> run/meta */
  var metaEls = {logic: document.getElementById('f-logic'), macos: document.getElementById('f-macos'), kb: document.getElementById('f-kb')};
  var metaTimer, metaQ = Promise.resolve();
  Object.keys(metaEls).forEach(function (k) {
    metaEls[k].addEventListener('input', function () {
      clearTimeout(metaTimer);
      metaTimer = setTimeout(function () {
        var m = {logic: metaEls.logic.value.trim(), macos: metaEls.macos.value.trim(), kb: metaEls.kb.value.trim()};
        window.__meta = m;
        if (db) metaQ = metaQ.then(function () { return db.doc('run/meta').set(m); }).catch(function () {});
      }, 700);
    });
  });

  ITEMS.forEach(function (it) { paint(it.id); });
  stats(); filter();

  /* ---------- connect the store ---------- */
  if (!window.claude || !window.claude.use) { document.getElementById('offline').hidden = false; return; }
  window.claude.use('db').then(function (d) {
    if (!d) {
      document.getElementById('offline').hidden = false;
      document.querySelectorAll('.acts button').forEach(function (b) { b.disabled = true; });
      return;
    }
    db = d;
    db.collection('results').onSnapshot(function (snap) {
      snap.docChanges().forEach(function (ch) {
        var id = ch.doc.id; if (!els[id]) return;
        if (ch.type === 'removed') delete results[id]; else results[id] = ch.doc.data();
        paint(id);
      });
      stats(); filter();
    }, function () { document.getElementById('offline').hidden = false; });
    db.doc('run/meta').onSnapshot(function (s) {
      if (!s.exists) return;
      var m = s.data(); window.__meta = m;
      Object.keys(metaEls).forEach(function (k) { if (document.activeElement !== metaEls[k]) metaEls[k].value = m[k] || ''; });
    }, function () {});
  });
})();
</script>
"""


def main():
    data, total = items()
    for it in data:
        it["kh"] = keycap(it["k"]) if it["k"] else ""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    OUT.write_text(PAGE.replace("__DATA__", blob), encoding="utf-8")
    n = {p: sum(1 for d in data if d["id"].startswith(p)) for p in ("s-", "k-", "t-")}
    print(f"Wrote {OUT}  ({OUT.stat().st_size // 1024} KB)  items: {len(data)} "
          f"({n['t-']} tricks, {n['s-']} steps, {n['k-']} key rows)")


if __name__ == "__main__":
    main()
