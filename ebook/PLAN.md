# Selling plan — Logic Pro Crash Course

How to sell this, and what to build in what order.

The short version: **stop selling a PDF and start selling access.** The searchable
web library becomes the product; the PDF ships alongside it as the offline copy.
That is a better product, it is easier to keep correct, and it is worth more than
$14.99 rather than exactly $14.99.

---

## 1. Why the web version should be the product

The book's own promise is "use while producing." Nobody reads 265 tricks front to
back — they hit a problem, search, take the trick, get back to the music. A PDF
answers that badly: you scroll, or you use a viewer's find, and you cannot filter.

The web version answers it directly, and it is already built. `build_site_page.py`
produces a page with live search across every trick, a Game-changers filter, `/`
to focus the search box, sticky section nav, and the portfolio's reveal animations.

Three further advantages, in order of how much they matter:

1. **It can be corrected.** This book has already lost 99 tricks to a verification
   pass and 119 more were rewritten. More will change — Logic ships updates and
   Apple renames things. A PDF sold in March is wrong by September and every buyer
   holds the wrong copy. A web library is fixed once and everyone has the fix.
2. **"Lifetime access, including updates" justifies the price.** A static PDF at
   $14.99 competes with free blog posts. A maintained, searchable reference does not.
3. **It is a portfolio piece.** It lives on the portfolio site, in the portfolio's
   design language, and demonstrates the work directly.

Keep shipping the PDF too. It costs nothing — it is already built — it works on a
plane, and "web library + PDF" is a visibly better offer than either alone.

---

## 2. Three surfaces

| Surface | URL | Public? | Contains |
| --- | --- | --- | --- |
| **Free sample** | `/logic-pro-tips` | Yes, indexed | ~25 tricks, full search UI |
| **Sales page** | `/logic-pro-crash-course` | Yes, indexed | Pitch, preview tricks, price |
| **Library** | `/library` | Token-gated | All 265 tricks + PDF link |

The **free sample is the marketing**, not a giveaway. A paid-only page has no SEO —
Google cannot index what it cannot reach, so a purely gated product has no organic
top of funnel at all. The sample fixes that and does something the sales page
cannot: it lets someone *use* the search, find a trick that solves their actual
problem, and learn the thing works before paying. Twenty-five tricks is enough to
be genuinely useful and not enough to replace the product.

Pick sample tricks that are useful but not the crown jewels — no `GAME CHANGER`
badges in the free set.

---

## 3. Architecture

The site is static on Netlify with `publish = "."`, so **everything in the repo is
public**. That single fact drives the whole design.

```
IN THE REPO (public, served by Netlify)
  logic-pro-crash-course.html   sales page
  logic-pro-tips.html           free sample — 25 tricks baked in, fine to be public
  library.html                  SHELL ONLY: design, search UI, animations, zero tricks
  netlify/functions/*.js        checkout, webhook, library, download

NEVER IN THE REPO (private object storage / function-side)
  library-content.json          all 265 tricks — fetched at runtime after auth
  logic-pro-crash-course.pdf    served only via short-lived signed URL
```

`library.html` is a skeleton. Open it logged out and there is nothing to read. It
fetches its content from a function that checks the caller paid first.

> There is currently an untracked copy of the PDF at
> `assets/resources/logic-pro-crash-course.pdf` in the site repo. It has never been
> committed, so nothing has leaked — but delete it or gitignore it before anyone
> runs `git add -A`.

---

## 4. Purchase to access

```
Buyer clicks Get instant access
   └─> /buy  ──redirect──> functions/checkout
         creates a Stripe Checkout Session (mode: payment), 303 to session.url

Stripe hosts the payment page (3DS/SCA handled, you stay out of PCI scope)

Payment succeeds
   └─> Stripe POSTs checkout.session.completed ──> functions/webhook
         VERIFY THE SIGNATURE (stripe.webhooks.constructEvent)
         mint a random 32-byte access key
         store  key -> { email, session_id, created, revoked:false, hits:0 }
         email the buyer:  https://…/library?k=<key>

Buyer opens the link
   └─> library.html reads ?k=, saves it to localStorage, strips it from the URL
   └─> POST functions/library { key }  ->  validates  ->  returns the tricks JSON
   └─> page renders and search runs client-side over that JSON

PDF download
   └─> POST functions/download { key } -> signed URL, 15–60 min expiry
```

**Three rules, all load-bearing:**

1. **Fulfil from the verified webhook, never from the success page.** The success
   URL is a plain URL — it can be guessed, shared, or bookmarked. It is not proof
   of payment. If the success page shows anything, it must look up the
   `session_id` server-side and confirm `payment_status === "paid"`.
2. **Verify the webhook signature.** An unverified endpoint is a URL anyone can POST
   to. Without `constructEvent` and the signing secret, someone can mint themselves
   a purchase.
3. **The content function is the security boundary.** Not the page. Anyone can read
   `library.html`; the only thing that matters is that the function refuses to hand
   over the JSON without a valid key.

**Why a stored key rather than a signed JWT:** you can revoke it. A JWT is valid
until it expires, so a key posted on a forum works until then. A stored key dies the
moment you flip `revoked`.

---

## 5. Abuse, honestly scoped

Any buyer can open devtools and save the JSON. That is true of every digital
product — a PDF can be uploaded to a forum just as easily. **The goal is friction
and revocability, not DRM**, and DRM at this price point costs more than it saves
and punishes legitimate buyers.

Worth building, cheap:

- Rate-limit content fetches per key (60/hour is generous for real use)
- Count distinct IPs per key; flag anything above ~5 for a look
- Cap PDF downloads per key (5 is plenty)
- A one-line way for you to revoke a key and re-issue it

Not worth building: obfuscation, canvas rendering, disabling right-click, watermarking
per buyer. All defeated in minutes, all degrade the product.

---

## 6. Build order

Each phase ships something usable. Do not build 2 and 3 in parallel — payment
without delivery is worse than neither.

**Phase 0 — finish the accuracy work.** *(me, before launch)*
119 of the 265 surviving tricks are rewrites that were never adversarially
re-checked. Close that first. Selling a reference whose corrections are unverified
is the one thing that produces exactly the refund emails you want to avoid.

**Phase 1 — free sample page.** *(me to build, site agent to deploy)*
Public, indexed, real search UI, 25 non-headline tricks. Ships before payment
exists and starts earning SEO immediately, which takes months to mature — so it
should go up first, not last.

**Phase 2 — payment and delivery.** *(site agent)*
`checkout` + signature-verified `webhook` + key issuance + purchase email. Test with
`4242 4242 4242 4242`. At the end of this phase you can take money and deliver the
PDF by signed URL. **You could launch here** if you want revenue sooner — the PDF
alone is a complete product.

**Phase 3 — the gated library.** *(me for the shell + content build, site agent for the function)*
`library.html` + `functions/library`. This is the upgrade that justifies the price
and the "lifetime updates" line.

**Phase 4 — post-launch.**
Add a visible "last updated" date to the library. When Logic ships an update,
correct the content, redeploy, and email buyers that it changed — that email is
what makes lifetime access feel like something they bought rather than something
they were promised.

---

## 7. Who builds what

**Me, in this repo:**
- `build_sample_page.py` → the free 25-trick page
- `build_library.py` → `library.html` (shell, no content) + `library-content.json`
- Reference implementations of the four functions, in `HANDOFF.md`
- The Phase 0 verification pass

**Site agent, in `dannnymcccarthy-site`:**
- Deploy the pages, add sitemap entries
- Write and wire the four Netlify functions
- Stripe product/price, webhook endpoint, signing secret
- Private storage bucket, signed URL generation
- Purchase email

**You:**
- Stripe account, product, price object
- Delete the stray PDF from the site repo
- The two business decisions below

---

## 8. Open decisions

| Decision | Why it is yours |
| --- | --- |
| **Tax** | With Stripe you are the merchant of record. Digital downloads can trigger VAT/GST/US sales tax depending on where buyers are. Stripe Tax can calculate and collect; registering and filing is still on you. A merchant-of-record platform (Lemon Squeezy, Paddle, Gumroad) absorbs this for a higher fee — but that is a different build. |
| **EU consent** | In the EU a buyer normally has a 14-day withdrawal right on distance sales. The usual exemption for instantly-delivered digital content is an explicit checkout consent to immediate delivery. Stripe Checkout supports it. Legal question, not a design one. |
| **Refunds** | Previously decided against stating a policy. Worth revisiting only because with a *hosted library* you can revoke access on refund, which makes offering one much safer than it is with a PDF. |
| **Price** | $14.99 is right for a PDF. A maintained searchable library with lifetime updates supports more. Raising it later is easier than lowering it. |

---

## 9. Honest limits

- **The accuracy floor is what it is.** Everything in the book was checked against
  Apple's documentation as reached through search results, not the manual itself.
  Allowlisting `help.apple.com` in the build environment would fix that properly.
- **A gated library needs email to work.** If purchase emails land in spam, buyers
  cannot reach what they bought. Use a real transactional sender (Postmark, Resend,
  SES) with SPF/DKIM on the domain — not raw SMTP from a function.
- **Every hardcoded number drifts.** Trick counts, page counts and the version claim
  are all derived from `content/` and the built PDF for exactly this reason. Anything
  the site agent hardcodes into the site will be wrong within a month. Have it read
  the numbers from the page it is given, not retype them.
