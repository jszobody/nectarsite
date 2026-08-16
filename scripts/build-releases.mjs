#!/usr/bin/env node
// Generates the update artifacts consumed by `vite build`:
//
//   updates/<slug>/index.html        ← a Vite HTML entry (see vite.config.js)
//   updates/<slug>/embed/index.html  ← ditto, chrome-free, framed by the app
//   public/whats-new.json            ← copied verbatim into dist/
//
// All three are generated, gitignored, and rewritten from scratch on every run.
import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadReleases, whatsNewPayload } from './releases.mjs'
import { fullPage, embedPage } from './templates.mjs'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const releases = loadReleases(join(root, 'content/releases'))

// Rebuild from scratch so a deleted or renamed content file can't leave a stale
// page published.
rmSync(join(root, 'updates'), { recursive: true, force: true })

for (const release of releases) {
  const dir = join(root, 'updates', release.slug)
  mkdirSync(join(dir, 'embed'), { recursive: true })
  writeFileSync(join(dir, 'index.html'), fullPage(release))
  writeFileSync(join(dir, 'embed/index.html'), embedPage(release))
}

mkdirSync(join(root, 'public'), { recursive: true })
writeFileSync(
  join(root, 'public/whats-new.json'),
  JSON.stringify(whatsNewPayload(releases), null, 2) + '\n',
)

console.log(
  `[updates] generated ${releases.length} page(s): ${releases.map((r) => `${r.slug} (${r.version})`).join(', ')}`,
)
