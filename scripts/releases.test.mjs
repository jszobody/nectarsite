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
  const r = parseRelease(VALID, '0.6.0.md')
  assert.equal(r.version, '0.6.0')
  assert.equal(r.date, '2026-08-14')
  assert.equal(r.headline, 'Data Rules')
  assert.equal(r.feature, true)
  assert.deepEqual(r.summary, ['First bullet'])
})

test('parseRelease derives both URLs from the version', () => {
  const r = parseRelease(VALID, '0.6.0.md')
  assert.equal(r.url, 'https://nectardocs.com/releases/0.6.0/')
  assert.equal(r.embedUrl, 'https://nectardocs.com/releases/0.6.0/embed/')
})

test('parseRelease renders the body to HTML', () => {
  const r = parseRelease(VALID, '0.6.0.md')
  assert.match(r.bodyHtml, /<strong>text<\/strong>/)
})

test('parseRelease passes raw HTML through', () => {
  const src = VALID.replace('Body **text**.', '<video src="https://x/y.mp4" controls></video>')
  assert.match(parseRelease(src, '0.6.0.md').bodyHtml, /<video src="https:\/\/x\/y\.mp4"/)
})

test('parseRelease rejects a filename that disagrees with the version', () => {
  assert.throws(() => parseRelease(VALID, '0.7.0.md'), /filename/)
})

for (const field of ['version', 'date', 'headline']) {
  test(`parseRelease rejects a missing ${field}`, () => {
    const src = VALID.replace(new RegExp(`^${field}:.*$`, 'm'), '')
    assert.throws(() => parseRelease(src, '0.6.0.md'), new RegExp(field))
  })
}

test('parseRelease rejects an empty summary', () => {
  const src = VALID.replace('summary:\n  - "First bullet"', 'summary: []')
  assert.throws(() => parseRelease(src, '0.6.0.md'), /summary/)
})

test('parseRelease defaults feature to false', () => {
  const src = VALID.replace('feature: true\n', '')
  assert.equal(parseRelease(src, '0.6.0.md').feature, false)
})

test('compareVersions orders numerically, not lexically', () => {
  assert.ok(compareVersions('0.9.0', '0.10.0') < 0)
  assert.ok(compareVersions('0.10.0', '0.9.0') > 0)
  assert.equal(compareVersions('1.2.3', '1.2.3'), 0)
  assert.ok(compareVersions('1.0.0', '0.99.99') > 0)
})

test('whatsNewPayload strips the body and sorts newest-first', () => {
  const a = parseRelease(VALID, '0.6.0.md')
  const b = parseRelease(VALID.replace(/0\.6\.0/g, '0.10.0'), '0.10.0.md')
  const payload = whatsNewPayload([a, b])
  assert.deepEqual(payload.releases.map((r) => r.version), ['0.10.0', '0.6.0'])
  assert.equal('bodyHtml' in payload.releases[0], false)
})
