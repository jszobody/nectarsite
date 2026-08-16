// HTML for the two generated page types. The head/header/footer markup mirrors
// index.html so a release page looks like the rest of nectardocs.com.
const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const prettyDate = (iso) => {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

// Tailwind's typography plugin isn't installed, so the prose styles are explicit.
// Scoped to .prose-notes; shared by both page types.
const PROSE = `
      .prose-notes h2 { margin-top: 2.5rem; margin-bottom: 0.75rem; font-size: 1.375rem; font-weight: 600; letter-spacing: -0.01em; color: var(--notes-heading); }
      .prose-notes h3 { margin-top: 2rem; margin-bottom: 0.5rem; font-size: 1.125rem; font-weight: 600; color: var(--notes-heading); }
      .prose-notes p { margin-bottom: 1.125rem; line-height: 1.75; }
      .prose-notes ul { margin: 0 0 1.125rem 1.25rem; list-style: disc; }
      .prose-notes ol { margin: 0 0 1.125rem 1.25rem; list-style: decimal; }
      .prose-notes li { margin-bottom: 0.5rem; line-height: 1.7; padding-left: 0.25rem; }
      .prose-notes strong { font-weight: 600; color: var(--notes-heading); }
      .prose-notes a { color: var(--notes-accent); text-decoration: underline; text-underline-offset: 2px; }
      .prose-notes code { font-family: var(--font-mono, ui-monospace, monospace); font-size: 0.875em; padding: 0.1em 0.35em; border-radius: 4px; background: var(--notes-code-bg); color: var(--notes-heading); }
      .prose-notes img, .prose-notes video { display: block; width: 100%; height: auto; margin: 1.75rem 0; border-radius: 10px; border: 1px solid var(--notes-rule); }
      .prose-notes hr { margin: 2rem 0; border: 0; border-top: 1px solid var(--notes-rule); }
`

export function fullPage(release) {
  return `<!doctype html>
<html lang="en" class="scheme-only-dark">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" type="image/svg+xml" href="/nectar-n.svg" />
    <title>Nectar ${esc(release.version)} · ${esc(release.headline)}</title>
    <meta name="description" content="${esc(release.summary[0])}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Nectar ${esc(release.version)} · ${esc(release.headline)}" />
    <meta property="og:description" content="${esc(release.summary[0])}" />
    <meta property="og:url" content="${esc(release.url)}" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500&family=Geist:wght@300..700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/src/main.css" />
    <style>
      :root {
        --notes-heading: #ffffff;
        --notes-accent: #ffa31f;
        --notes-rule: rgb(255 255 255 / 0.1);
        --notes-code-bg: rgb(255 255 255 / 0.08);
      }
${PROSE}
    </style>
  </head>
  <body class="min-h-dvh bg-ink-950 font-sans text-zinc-300 antialiased">
    <div class="isolate">
      <header class="sticky top-0 z-50 border-b border-white/10 bg-ink-950/80 backdrop-blur">
        <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
          <a href="/" aria-label="Homepage" class="flex items-center gap-2.5">
            <img src="/nectar-n.svg" alt="" class="h-10 w-auto shrink-0" />
            <span class="text-lg font-semibold tracking-tight text-white">Nectar</span>
          </a>
          <nav class="flex items-center gap-1 text-sm">
            <a href="/download.html" class="rounded-md px-3 py-2 font-medium text-zinc-400 hover:text-white">Download</a>
          </nav>
        </div>
      </header>

      <main class="mx-auto max-w-3xl px-6 py-16">
        <p class="font-mono text-xs tracking-wide text-zinc-500 uppercase">
          Version ${esc(release.version)} · ${esc(prettyDate(release.date))}
        </p>
        <h1 class="mt-3 text-4xl font-semibold tracking-tight text-balance text-white">${esc(release.headline)}</h1>
        <ul role="list" class="mt-6 flex flex-col gap-2 border-l-2 border-nectar-500 pl-5">
          ${release.summary.map((s) => `<li class="text-base/7 text-zinc-400">${esc(s)}</li>`).join('\n          ')}
        </ul>
        <div class="prose-notes mt-12 text-base text-zinc-300">
${release.bodyHtml}
        </div>
        <p class="mt-16 border-t border-white/10 pt-8 text-sm text-zinc-500">
          Nectar updates itself — you'll get this automatically.
          <a href="/download.html" class="text-nectar-400 hover:text-nectar-300">Download</a> if you're setting up a new machine.
        </p>
      </main>

      <footer class="border-t border-white/10">
        <div class="mx-auto max-w-6xl px-6 py-10">
          <a href="/" aria-label="Homepage" class="inline-flex items-center gap-2.5">
            <img src="/nectar-n.svg" alt="" class="h-6 w-auto shrink-0" />
            <span class="text-base font-semibold tracking-tight text-white">Nectar</span>
          </a>
          <p class="mt-6 text-sm text-zinc-500">© 2026 Signature Tech Studio, Inc.</p>
        </div>
      </footer>
    </div>
  </body>
</html>
`
}

// The page the desktop app frames. No site chrome, no nav, no footer — the
// dialog supplies all of that. Deliberately standalone: it carries its own
// palette (nectardocs.com is dark-only, the app is not) and its own CSS, so it
// does not depend on the marketing site's Tailwind build and cannot be broken by
// a redesign of it.
//
// Theme arrives as ?theme=light|dark, read at parse time. The app's dark mode is
// independent of the OS setting, so prefers-color-scheme would be wrong whenever
// the two disagree.
export function embedPage(release) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Nectar ${esc(release.version)} · ${esc(release.headline)}</title>
    <meta name="robots" content="noindex" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500&family=Geist:wght@300..700&display=swap" rel="stylesheet" />
    <style>
      :root {
        --font-mono: "Geist Mono", ui-monospace, monospace;
        --notes-bg: #ffffff;
        --notes-text: #3d3d3d;
        --notes-heading: #1a1a1a;
        --notes-muted: #707070;
        --notes-accent: #b35c00;
        --notes-rule: rgb(0 0 0 / 0.1);
        --notes-code-bg: rgb(0 0 0 / 0.05);
      }
      html.theme-dark {
        --notes-bg: #1f1f1f;
        --notes-text: #d6d6d6;
        --notes-heading: #ffffff;
        --notes-muted: #9a9a9a;
        --notes-accent: #ffa31f;
        --notes-rule: rgb(255 255 255 / 0.1);
        --notes-code-bg: rgb(255 255 255 / 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        padding: 22px 26px 32px;
        background: var(--notes-bg);
        color: var(--notes-text);
        font-family: "Geist", ui-sans-serif, system-ui, sans-serif;
        font-size: 14px;
        -webkit-font-smoothing: antialiased;
      }
      .eyebrow { margin: 0; font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--notes-muted); }
      h1 { margin: 8px 0 0; font-size: 26px; font-weight: 600; letter-spacing: -0.02em; color: var(--notes-heading); }
      .summary { margin: 18px 0 0; padding: 0 0 0 16px; border-left: 2px solid var(--notes-accent); list-style: none; }
      .summary li { margin-bottom: 6px; color: var(--notes-muted); line-height: 1.6; }
      .prose-notes { margin-top: 30px; }
${PROSE}
    </style>
  </head>
  <body>
    <p class="eyebrow">Version ${esc(release.version)} · ${esc(prettyDate(release.date))}</p>
    <h1>${esc(release.headline)}</h1>
    <ul class="summary">
      ${release.summary.map((s) => `<li>${esc(s)}</li>`).join('\n      ')}
    </ul>
    <div class="prose-notes">
${release.bodyHtml}
    </div>
    <script>
      // Theme from the query string (see the comment above).
      if (new URLSearchParams(location.search).get('theme') === 'dark') {
        document.documentElement.classList.add('theme-dark')
      }
      // Without this a link inside the frame navigates the whole page into a
      // narrow panel with no way back.
      for (const a of document.querySelectorAll('a[href]')) {
        a.target = '_blank'
        a.rel = 'noopener noreferrer'
      }
    </script>
  </body>
</html>
`
}
