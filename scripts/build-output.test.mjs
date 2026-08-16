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
    assert.match(r.url, /^https:\/\/nectardocs\.com\/releases\/.+\/$/, 'url')
    assert.match(r.embedUrl, /^https:\/\/nectardocs\.com\/releases\/.+\/embed\/$/, 'embedUrl')
    assert.equal('bodyHtml' in r, false, 'body must never enter the JSON')
  }
})

test('every release publishes both pages', () => {
  for (const r of payload.releases) {
    assert.ok(existsSync(join(dist, 'releases', r.version, 'index.html')), `${r.version} full page`)
    assert.ok(existsSync(join(dist, 'releases', r.version, 'embed/index.html')), `${r.version} embed page`)
  }
})

test('the embed page carries no site chrome', () => {
  const html = readFileSync(join(dist, 'releases', payload.releases[0].version, 'embed/index.html'), 'utf8')
  assert.equal(html.includes('<header'), false)
  assert.equal(html.includes('<footer'), false)
})
