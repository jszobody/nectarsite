# nectardocs.com redesign — design spec

Date: 2026-07-30 · Status: approved by Joseph (conversation), implementation next

## Goal

Beta lead-gen, but impressive: the site's job is to make Nectar look serious and
deeply understood, and convert reprographics / AEC document-control shops into
quality beta requests. Success = a shop owner or doc-control lead scrolls the page
and thinks "these people understand my workflow," then submits the form.

## Decisions (locked)

- **Architecture:** single long-form homepage carrying the entire pitch. Download,
  Terms, Privacy remain as utility pages, reskinned to match. Security is a
  *section* of the homepage, not a page.
- **Visual identity:** evolve the existing dark identity (ink slate + nectar
  orange/gold, Geist/Geist Mono, blueprint motif) — execute it at a much higher
  level rather than replace it.
- **Product visuals:** faithful animated HTML/CSS recreations of the real app UI.
  No screenshots.
- **Stack:** stay Vite + Tailwind 4, static on GitHub Pages (deploy.yml on push to
  main). Vanilla JS animation modules only; no frameworks, no animation libraries.
  HubSpot form embed stays (portal 21331419) but restyled to match.
- **No invented numbers:** every claim on the page must be a product truth
  (feature, policy, architecture). No fake testimonials, logos, or stats.

## Page structure (index.html)

Narrative arc: pain → watch it get solved → how it works (depth) → built for your
hands → what you get out → why you can trust it → FAQ → request access.

1. **Header** — sticky, blur backdrop. Logo, anchors (How it works · Review ·
   Security · FAQ), Download link, orange "Request beta access" CTA.
2. **Hero + live demo.** Headline stays "Stop hand-naming scanned drawings."
   Centerpiece: animated recreation of the real app window — rows of
   `scan_00NN.pdf` appear, status pills walk Uploading → Inspecting → Verifying,
   sheet number/title type in with amber "auto" markers, one uncertain row flips
   to Review, filename column morphs to `A-101 - First Floor Plan.pdf`. Plays on
   scroll-into-view, loops; `prefers-reduced-motion` gets the finished state.
3. **Fact band** — three product truths: hundreds of sheets per drop · confident
   reads sail through / uncertain ones wait for review · files purged from cloud
   within 72 hours.
4. **"How it reads a sheet"** — five scroll-animated pipeline steps:
   drop (resumable, per-file retry) → high-res OCR (searchable PDF byproduct) →
   AI reads the title block (text pass first, vision pass on the title-block crop
   only when needed, inside our own AWS network) → deterministic guards
   (discipline-prefix checks, rotation-aware reading, drawing-index cross-checks)
   → review only the uncertain (bad extraction refunds its credit).
5. **The review loop** — "Built for the person doing 400 sheets before lunch."
   Side-by-side viewer+fields visual, animated keycaps (⌘/Ctrl+Enter accept &
   next), OCR overlay click-line-to-fill, snap-to-title-block.
6. **What comes out** — filename template editor with token pills ({prefix},
   {sheet_number}, {sheet_title}), rename-in-place (non-destructive), export
   folder of searchable PDFs, automation modes for trusted sets.
7. **Security & residency band** — four pillars: in-network AI (never leaves our
   cloud, no third-party AI vendors, never trains models) · 72-hour purge ·
   US + Canada data planes (account pinned to region) · non-destructive by design
   + signed/notarized builds. Written to survive an IT-approval email screenshot.
8. **FAQ** — 6–8: usage-based pricing (credits only, pay for what you process,
   volume discounts — never "free during beta", some users already pay), credits
   & refund-on-miss, platforms, seats/licensing, what happens to files, what
   sets it handles, Canada.
9. **Beta form** — restyled HubSpot embed + one-business-day promise.
10. **Footer** — columns: product, legal, company (Signature Tech Studio).

## Visual system

- Deepen the ink scale for contrast range; nectar orange/gold strictly as accent.
- Drafting-sheet language: cards framed like drawing sheets (thin border + title
  strip), mono annotation labels, dimension-line dividers, crosshair corner
  ticks, subtler blueprint grid than today.
- Motion: IntersectionObserver-driven CSS reveals + one vanilla-JS state machine
  for the hero demo. All motion honors `prefers-reduced-motion`.

## Out of scope

Pricing page, real screenshots, testimonials/logos, CMS, framework migration,
replacing HubSpot. Tos/privacy get only cosmetic consistency touch-ups.

## Verification

Local `npm run dev`, drive with dev-browser at 1440/1024/390 widths, screenshot
every section, check reduced-motion and keyboard nav. No push to main (= deploy)
until Joseph approves the result in a browser.
