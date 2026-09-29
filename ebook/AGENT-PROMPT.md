# Prompt to paste into the new chat

Copy everything below the line, and attach `HANDOFF.md`, `logic-pro-crash-course-sales.html`
and the four cover files from `dist/store/` (`logic-pro-crash-course.png`, `.webp`,
`logic-pro-crash-course-wide.png`, `.webp`).
**Do not attach the PDF or the library HTML** — they are the paid product and only go to Gumroad.

---

I want to add a digital product to the store on my portfolio site. Please read the attached
`HANDOFF.md` first — it is the spec, and it contains constraints that will not be obvious from
the code.

**The product:** *Logic Pro Crash Course*, 248 tricks, an 89-page PDF plus a searchable
library file. **$9 USD, one-time.** It is sold through my existing **Gumroad** store, the same
way as my plug-ins, at `dannnymcccarthy.gumroad.com/l/logic-pro-crash-course`. I am setting up
the Gumroad product myself.

**My site:** `dannymac2334/dannnymcccarthy-site` — static HTML on Netlify, `publish = "."`.

**What I need done:**

1. Add the attached page as `store/logic-pro-crash-course.html`, and the covers to
   `store/covers/` and `store/covers-wide/`.
2. Add a card for it to `store/index.html` (markup is in the handoff) and to that page's
   `ItemList` JSON-LD.
3. Add the URL to `sitemap.xml`.

**Things that must be true when you are done:**

- No checkout code, webhook, function or file storage was added. Gumroad handles payment and
  delivery.
- Neither the PDF nor the library HTML is anywhere in the repo.
- The page is added as given: not wrapped in the site header/footer, not hand-edited, and the
  Apple notice at the bottom is still there.

**Before you change anything,** show me the list of files you will add or edit. When it is
done, walk me through the verification checklist at the end of `HANDOFF.md`.
