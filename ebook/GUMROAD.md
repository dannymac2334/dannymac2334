# Gumroad listing — Logic Pro Crash Course

Everything to set up the product in your existing Gumroad account
(`dannnymcccarthy.gumroad.com`), in the order Gumroad asks for it. The sales page on your
site already links to the permalink below, so use it exactly.

Build the files first: `python3 package_gumroad.py` (after the normal build, see README).

---

## 1. New product

| Field | Value |
| --- | --- |
| Type | Digital product |
| Name | `Logic Pro Crash Course` |
| Price | `$9` (not pay-what-you-want) |
| Custom URL / permalink | `logic-pro-crash-course` → `dannnymcccarthy.gumroad.com/l/logic-pro-crash-course` |

## 2. Files to upload (Content tab)

From `ebook/dist/gumroad/` (git-ignored, because it is the paid product):

1. `Logic-Pro-Crash-Course.pdf` — the book, 89 pages
2. `Logic-Pro-Crash-Course-Library.html` — the searchable library; opens in any browser, works offline

Put this line above the files in the Content tab so buyers know what the second one is:

> Open **Logic-Pro-Crash-Course-Library.html** in any browser to search all 249 tricks by what
> you want to do. It works offline. The PDF is the same book, for reading and printing.

## 3. Cover and thumbnail

From `ebook/dist/store/`:

- Cover: `gumroad-cover-1280x720.png`
- Thumbnail: `gumroad-thumb-600.png`

## 4. Description (paste as is)

> **249 Logic Pro tricks that actually work, and every one cites its source.**
>
> Logic can already do the thing you need. This is where it lives: 249 tricks across 19
> sections, from setting up Logic to mixing and exporting, each short enough to read in ten
> seconds and use straight away.
>
> **New to Logic?** It starts from zero. Start Here walks you through your first session in
> ten steps, 40 tricks are marked safe for your first day, and every Logic word the book uses
> is explained in plain English in a 48-word glossary.
>
> **Find it by what you're making.** Open the searchable library and type what you want to
> do (record vocals, make a beat, fix my timing) and the right tricks come up first.
>
> **Checked, not guessed.** Every trick shows the source it was checked against, usually
> Apple's own Logic Pro guide, with a live link. Anything that could not be confirmed was cut.
>
> **What you get**
> - The PDF: 89 pages, clickable contents, bookmarks for every section
> - The searchable library: one file, opens in any browser, works offline
> - Covers Logic Pro 11 and 12, stock Logic only, no plug-ins to buy
>
> *Logic Pro Crash Course is an independent publication and has not been authorized,
> sponsored, or otherwise approved by Apple Inc. Apple, Logic Pro, Mac, macOS, MainStage, iPad
> and Finder are trademarks of Apple Inc., registered in the U.S. and other countries and
> regions.*

The Apple notice at the end is required on "related materials" by Apple's guidelines for
third-party publications. Keep it.

## 5. Receipt (Settings → customize the receipt message)

> Thanks for picking up Logic Pro Crash Course. Start with the library file: type what you want
> to do and the right tricks come up first. New to Logic? Open it and tap Start here.
> Found something that doesn't match your version of Logic? Reply to this email and tell me.

## 6. Do not add

- **No refund guarantee** or "money back" line in the description or receipt. You decided
  against stating one. (Gumroad's own policy still applies to disputes.)
- **No "about the author" / credits** section.
- **No Apple logo or Logic Pro app icon**, in the cover or anywhere else.
- **No crossed-out "was" price.**

## 7. Check before you publish

- [ ] Buy it yourself (or use a 100%-off discount code) and confirm both files download
- [ ] Open the library file from your Downloads folder: search works, "Start here" works
- [ ] The receipt email reads right
- [ ] `dannnymcccarthy.gumroad.com/l/logic-pro-crash-course` opens the product
- [ ] Then publish, and ask the site agent to add the store page (`HANDOFF.md`)

## To confirm with Gumroad (not decided here)

- **Tax.** Gumroad says it acts as merchant of record and handles sales tax and VAT on your
  sales; confirm this is on for your account in Gumroad's settings.
- **EU buyers.** The EU normally gives a 14-day withdrawal right on distance sales unless the
  buyer consents to immediate delivery of digital content. Check how Gumroad handles that
  consent at checkout.
