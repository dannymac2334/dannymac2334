# Handoff — add "Logic Pro Crash Course" ($9) to the store on dannnymcccarthy.com

Paste this whole file to the agent doing the site work, and attach:

- `logic-pro-crash-course-sales.html` (the product page)
- `store/logic-pro-crash-course.png`, `.webp` (1080×1080 card cover)
- `store/logic-pro-crash-course-wide.png`, `.webp` (1920×1080 banner, optional)

> **This replaces the earlier Stripe handoff.** The book is sold through the owner's existing
> **Gumroad** store, exactly like the plug-ins in `store/`. There is **no checkout code, no
> webhook, no serverless function and no file storage** to build. Gumroad takes the payment
> and delivers the files. If you started on Stripe functions for this, stop and remove them.

---

## What is being sold

*Logic Pro Crash Course*: 248 Logic Pro tricks as an 89-page PDF plus a searchable
library file, **$9 USD**, one-time, sold at
`https://dannnymcccarthy.gumroad.com/l/logic-pro-crash-course`. The owner sets up the Gumroad
product (see `GUMROAD.md` in the ebook folder); the buy buttons on the page already point
there.

## Repo

`dannymac2334/dannnymcccarthy-site` — static, Netlify (`publish = "."`, repo root is the web
root). Store products live in `store/`, one HTML page each, with covers in `store/covers/`.

---

## 1. Add the product page

| File you were given | Goes to |
| --- | --- |
| `logic-pro-crash-course-sales.html` | **`store/logic-pro-crash-course.html`** |
| `logic-pro-crash-course.png` / `.webp` | `store/covers/` |
| `logic-pro-crash-course-wide.png` / `.webp` | `store/covers-wide/` |

Live URL: `/store/logic-pro-crash-course` (the page's canonical already says so). Netlify
serves extensionless URLs, so no `_redirects` entry is needed.

The page is **self-contained**: its fonts, signature and styles are embedded. It deliberately
does not use the site's header, footer or `css/style.css`; it follows the owner's rates-page
design. Do not wrap it in the site chrome and do not hand-edit it (it is generated; edits are
overwritten). If copy needs to change, tell the owner.

## 2. Add it to the store index (`store/index.html`)

Add a card in the same markup as the plug-in cards:

```html
<a class="card reveal" href="/store/logic-pro-crash-course">
  <div class="thumb"><picture><source srcset="covers/logic-pro-crash-course.webp" type="image/webp"><img src="covers/logic-pro-crash-course.png" alt="Logic Pro Crash Course: 248 Logic Pro tricks, eBook cover" width="1080" height="1080" loading="lazy"></picture></div>
  <div class="cat">eBook · PDF + searchable library</div>
  <div class="name">Logic Pro Crash Course</div>
  <div class="pmeta-row"><span class="pprice">$9</span><span class="pshop">View book<svg class="ico ico-arr" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div>
  <p class="pdesc">248 Logic Pro tricks that actually work, each one citing its source. Starts from zero for beginners, and the library finds tricks by what you want to make.</p>
  <div class="ptags"><span class="ptag">Logic Pro 11 &amp; 12</span><span class="ptag">Beginner friendly</span><span class="ptag">Searchable</span></div>
</a>
```

Also add it to the `ItemList` JSON-LD at the top of `store/index.html` (next `position`,
`url` `https://www.dannnymcccarthy.com/store/logic-pro-crash-course`, `name`
`Logic Pro Crash Course`).

## 3. Sitemap

Add to `sitemap.xml`:

```xml
<url><loc>https://www.dannnymcccarthy.com/store/logic-pro-crash-course</loc></url>
```

## 4. The product files never go in the site repo

The PDF and the library HTML are the paid product. They are uploaded to Gumroad only. Do not
add either to the repo, to `store/downloads/`, or anywhere else Netlify serves. (The free
`VocalClean` installer in `store/downloads/` is a different case: it is free.)

## 5. Do not do these

1. **Do not build checkout, webhooks, functions or storage** for this product. Gumroad does it.
2. **Do not edit `css/style.css` or `js/main.js`** for this page. It needs neither.
3. **Do not reformat, minify or hand-edit the page.**
4. **Do not remove the Apple notice** at the bottom of the page ("…is an independent
   publication and has not been authorized, sponsored, or otherwise approved by Apple Inc."
   plus the trademark line). Apple's guidelines for third-party publications require it on the
   publication and all related materials:
   https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html.
   Do not add the Apple logo or the Logic Pro app icon anywhere, including the store card.

## 6. Verification checklist

- [ ] `/store/logic-pro-crash-course` loads, looks like the attached file, no console errors
- [ ] Both **Get it for $9** buttons open
      `https://dannnymcccarthy.gumroad.com/l/logic-pro-crash-course` (once the owner has
      published the Gumroad product; before then Gumroad shows a not-found page, which is
      expected)
- [ ] The store index shows the new card with its cover; the card links to the page
- [ ] `sitemap.xml` has the new URL
- [ ] View source: one `application/ld+json` `Product`, price `9.00`
- [ ] No PDF or library HTML anywhere in the repo: `git ls-files | grep -i "logic-pro-crash-course.*\.\(pdf\|html\)"`
      shows only `store/logic-pro-crash-course.html`
- [ ] The Apple notice is at the bottom of the page

## Page reference

- ~240 KB self-contained (Figtree and the signature are embedded), no external requests
- Sections: hero with price, the problem and the price card, six preview tricks, the
  19-section index, who it is and is not for, FAQ, final call to action
- The six preview tricks are real content from the book, deliberately; they do the selling
- `og:type` is `product`; JSON-LD is `Product` with an `Offer` at 9.00 USD

## Decided — do not add these

- **No refund promise.** No guarantee, "money back" or refund language on the page.
- **No bio or "who made this" section**, and no claims about the author's experience.
- **No crossed-out "was" price.**

## Still open (owner's decisions, not the site agent's)

- **A free sample page** for search traffic. Recommended, not built.
- **Where else the book is promoted** on the site (home page, nav, project pages).
