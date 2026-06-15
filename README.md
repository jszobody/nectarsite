# nectarsite

Marketing site for **Nectar** — `nectardocs.com`. Static, built with Vite + Tailwind v4,
deployed to GitHub Pages.

> Sibling repos live under `~/dev` (this is separate from the private Nectar product repo).

## Develop

```bash
npm install
npm run dev      # local dev server with live reload
npm run build    # outputs static site to dist/
npm run preview  # serve the built dist/ locally
```

## Pages

- `index.html` — landing page
- `tos.html` — Terms of Service (`/tos`)
- `privacy.html` — Privacy Policy (`/privacy`)

Shared styles/brand tokens: `src/main.css`. Static files (e.g. `CNAME`): `public/`.

## Deploy

Pushing to `main` builds and publishes via `.github/workflows/deploy.yml`
(GitHub Pages). Custom domain `nectardocs.com` is set via `public/CNAME`.
