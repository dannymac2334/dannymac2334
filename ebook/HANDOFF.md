# Handoff — publish "Logic Pro Crash Course" to dannnymcccarthy.com

Paste this whole file to the agent doing the site work, along with the two attached files.

---

## Goal

Publish a free resource page at **https://www.dannnymcccarthy.com/logic-pro-crash-course**,
with a downloadable PDF.

## Repo

`dannymac2334/dannnymcccarthy-site` — private, static, deployed on Netlify
(`netlify.toml` has `publish = "."`, so the repo root is the web root).

## Files supplied

| File you were given | Goes to | Notes |
| --- | --- | --- |
| `logic-pro-crash-course-page.html` | **`/logic-pro-crash-course.html`** (repo ROOT, next to `work.html`) | **Rename it** — drop the `-page` suffix. |
| `logic-pro-crash-course.pdf` | **`/assets/resources/logic-pro-crash-course.pdf`** | Create the `resources` folder. |

The page must sit at the repo **root**. It loads `css/style.css` and `js/main.js` by
relative path, and the download button points at `assets/resources/logic-pro-crash-course.pdf`.
Putting it in a subfolder breaks all three.

---

## Steps

### 1. Add the two files at the paths above.

### 2. Add one line to `sitemap.xml`

Insert alongside the other top-level pages (after the `/contact` entry):

```xml
<url><loc>https://www.dannnymcccarthy.com/logic-pro-crash-course</loc></url>
```

### 3. Do NOT add a `_redirects` entry

Netlify already serves extensionless URLs, so `/logic-pro-crash-course` resolves to
`logic-pro-crash-course.html` on its own. The existing `_redirects` file is only for 301s
from old Squarespace URLs — nothing to add there.

### 4. Optional — make it discoverable

Ask the owner before doing either of these; they change every page.

- **Footer link.** In the `Explore` column of `<footer class="foot">`, add:
  `<a href="logic-pro-crash-course.html">Logic Pro Course</a>`
  The footer is duplicated in every HTML file, so this is a find-and-replace across all of them.
- **Header nav link.** `<nav class="nav">` is likewise duplicated in every page. The nav is
  already 5 items; adding a 6th may crowd it at tablet widths. Check before committing.

---

## Constraints — please respect these

1. **Do not edit `css/style.css` or `js/main.js`.** The page needs no changes to either.
   All of its own CSS is inline in the page and scoped under `.lp`, so it cannot leak into
   other pages. Its only dependency on the site is:
   - `.reveal` / `.d1` / `.d2` / `.d3` classes, animated by the existing IntersectionObserver
     in `main.js`
   - `.site-head`, `.nav`, `.pill`, `.foot`, `.proj` from `style.css`
2. **Do not reformat or minify the page.** It is generated from a build script in a separate
   repo (`dannymac2334/dannymac2334`, `ebook/build_site_page.py`). Hand edits will be lost the
   next time it is regenerated. If content needs to change, say so rather than editing in place.
3. **Do not change the `<script>` block at the bottom of the page.** It runs the section
   jump-nav and the search filter, and is deliberately self-contained so it does not depend
   on markup elsewhere on the site.

---

## Known gotcha — PDF caching

`netlify.toml` sets `/assets/*` to `Cache-Control: public, max-age=31536000, immutable`.

That is correct for the images, but it means **if the PDF is ever replaced at the same path,
returning visitors will keep the old one for up to a year.** Two options — the owner should pick:

- Put the version in the filename on each update
  (`logic-pro-crash-course-v2.pdf`) and update the two links in the page, or
- Add a `netlify.toml` header block excluding `/assets/resources/*` from the immutable rule.

Nothing needs doing for the first publish. Flag it if a v2 ever ships.

---

## Verification checklist

After deploying, confirm:

- [ ] `https://www.dannnymcccarthy.com/logic-pro-crash-course` loads (no `.html` needed)
- [ ] Site header, nav and footer look identical to `work.html`
- [ ] Content fades in on scroll (that means `main.js` is reaching it)
- [ ] The sticky section bar highlights the current section as you scroll, and drags sideways
- [ ] Typing `marquee` in the search box shows **13 of 355 tricks**
- [ ] The **Game changers** toggle shows **61 of 355 tricks**
- [ ] Pressing `/` focuses the search box
- [ ] Both **Download the PDF** buttons return the 82-page PDF, not a 404
- [ ] Mobile: header collapses to the burger menu, cards go single column
- [ ] View source: one `application/ld+json` block, `@type: Article`

---

## Page reference

- 355 tricks, 19 sections, ~166 KB of HTML, no images, no build step
- Fonts come from the site's existing Poppins link — nothing new loaded
- `<title>`: `Logic Pro Crash Course | Dannny McCcarthy`
- Canonical + `og:url`: `https://www.dannnymcccarthy.com/logic-pro-crash-course`
- OG image reuses `assets/brand/og-cover.jpg`
- A `<noscript>` block disables the reveal animation if JS is blocked, so the page still
  renders in full rather than appearing blank
