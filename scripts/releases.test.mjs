import { test } from 'node:test'
import assert from 'node:assert/strict'
import { parseRelease, compareVersions, whatsNewPayload } from './releases.mjs'

const VALID = `---
version: "0.6.0"
date: "2026-08-14"
headline: "Data Rules"
feature: true
summary:
  - "First bullet"
---

Body **text**.
`

test('parseRelease lifts the frontmatter contract', () => {
  const r = parseRelease(VALID, 'data-rules.md')
  assert.equal(r.version, '0.6.0')
  assert.equal(r.date, '2026-08-14')
  assert.equal(r.headline, 'Data Rules')
  assert.equal(r.feature, true)
  assert.deepEqual(r.summary, ['First bullet'])
})

test('parseRelease routes by topic slug, not by version', () => {
  const r = parseRelease(VALID, 'data-rules.md')
  assert.equal(r.slug, 'data-rules')
  assert.equal(r.url, 'https://nectardocs.com/updates/data-rules/')
  assert.equal(r.embedUrl, 'https://nectardocs.com/updates/data-rules/embed/')
})

test('parseRelease renders the body to HTML', () => {
  const r = parseRelease(VALID, 'data-rules.md')
  assert.match(r.bodyHtml, /<strong>text<\/strong>/)
})

test('parseRelease passes raw HTML through', () => {
  const src = VALID.replace('Body **text**.', '<video src="https://x/y.mp4" controls></video>')
  assert.match(parseRelease(src, 'data-rules.md').bodyHtml, /<video src="https:\/\/x\/y\.mp4"/)
})

// The filename is the public URL, so it has to survive being one.
for (const bad of ['Data-Rules.md', 'data rules.md', 'data_rules.md', '0.7.0.md', '-data-rules.md']) {
  test(`parseRelease rejects the filename ${bad}`, () => {
    assert.throws(() => parseRelease(VALID, bad), /slug/)
  })
}

for (const field of ['version', 'date', 'headline']) {
  test(`parseRelease rejects a missing ${field}`, () => {
    const src = VALID.replace(new RegExp(`^${field}:.*$`, 'm'), '')
    assert.throws(() => parseRelease(src, 'data-rules.md'), new RegExp(field))
  })
}

test('parseRelease rejects an empty summary', () => {
  const src = VALID.replace('summary:\n  - "First bullet"', 'summary: []')
  assert.throws(() => parseRelease(src, 'data-rules.md'), /summary/)
})

test('parseRelease defaults feature to false', () => {
  const src = VALID.replace('feature: true\n', '')
  assert.equal(parseRelease(src, 'data-rules.md').feature, false)
})

test('compareVersions orders numerically, not lexically', () => {
  assert.ok(compareVersions('0.9.0', '0.10.0') < 0)
  assert.ok(compareVersions('0.10.0', '0.9.0') > 0)
  assert.equal(compareVersions('1.2.3', '1.2.3'), 0)
  assert.ok(compareVersions('1.0.0', '0.99.99') > 0)
})

test('whatsNewPayload strips the body and the slug, and sorts newest-first', () => {
  const a = parseRelease(VALID, 'data-rules.md')
  const b = parseRelease(VALID.replace(/0\.6\.0/g, '0.10.0'), 'other-thing.md')
  const payload = whatsNewPayload([a, b])
  assert.deepEqual(payload.releases.map((r) => r.version), ['0.10.0', '0.6.0'])
  assert.equal('bodyHtml' in payload.releases[0], false)
  // The app follows the published url/embedUrl and never assembles a path, which
  // is how the route moved without the app changing.
  assert.equal('slug' in payload.releases[0], false)
  assert.match(payload.releases[0].url, /\/updates\/other-thing\/$/)
})
