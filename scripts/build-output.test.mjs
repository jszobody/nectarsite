// Asserts what actually landed in dist/. Run AFTER `npm run build`.
// The JSON shape here is the cross-repo contract with the Nectar app — the
// matching assertion lives in frontend/src/lib/whatsNew.test.ts.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const dist = join(dirname(fileURLToPath(import.meta.url)), '../dist')
const payload = JSON.parse(readFileSync(join(dist, 'whats-new.json'), 'utf8'))

test('whats-new.json holds at least one release', () => {
  assert.ok(Array.isArray(payload.releases))
  assert.ok(payload.releases.length > 0)
})

test('every release matches the contract the app parses', () => {
  for (const r of payload.releases) {
    assert.equal(typeof r.version, 'string', 'version')
    assert.match(r.date, /^\d{4}-\d{2}-\d{2}$/, 'date')
    assert.ok(r.headline.length > 0, 'headline')
    assert.equal(typeof r.feature, 'boolean', 'feature')
    assert.ok(Array.isArray(r.summary) && r.summary.length > 0, 'summary')
    // Routed by topic, never by version. A /releases/<version>/ URL here means
    // the slug routing regressed.
    assert.match(r.url, /^https:\/\/nectardocs\.com\/updates\/[a-z0-9-]+\/$/, 'url')
    assert.match(r.embedUrl, /^https:\/\/nectardocs\.com\/updates\/[a-z0-9-]+\/embed\/$/, 'embedUrl')
    assert.equal('bodyHtml' in r, false, 'body must never enter the JSON')
    assert.equal('slug' in r, false, 'slug must never enter the JSON')
  }
})

// Derived from the published url, so this checks the JSON and the emitted files
// agree — the failure mode that leaves the app pointing at a 404.
const slugOf = (r) => r.url.replace(/\/$/, '').split('/').pop()

test('every update publishes both pages at its slug', () => {
  for (const r of payload.releases) {
    const slug = slugOf(r)
    assert.ok(existsSync(join(dist, 'updates', slug, 'index.html')), `${slug} full page`)
    assert.ok(existsSync(join(dist, 'updates', slug, 'embed/index.html')), `${slug} embed page`)
  }
})

test('the embed page carries no site chrome', () => {
  const html = readFileSync(join(dist, 'updates', slugOf(payload.releases[0]), 'embed/index.html'), 'utf8')
  assert.equal(html.includes('<header'), false)
  assert.equal(html.includes('<footer'), false)
})

test('the full page is canonical and the embed page defers to it', () => {
  const slug = slugOf(payload.releases[0])
  const full = readFileSync(join(dist, 'updates', slug, 'index.html'), 'utf8')
  const embed = readFileSync(join(dist, 'updates', slug, 'embed/index.html'), 'utf8')
  assert.ok(full.includes(`<link rel="canonical" href="${payload.releases[0].url}"`), 'full page canonical')
  assert.ok(embed.includes(`<link rel="canonical" href="${payload.releases[0].url}"`), 'embed canonical')
  assert.ok(embed.includes('name="robots" content="noindex"'), 'embed noindex')
})
