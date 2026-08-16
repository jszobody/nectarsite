// Pure parsing for release notes. Reads and validates; writes nothing.
// scripts/build-releases.mjs is the only thing that touches the filesystem.
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import matter from 'gray-matter'
import { marked } from 'marked'

export const SITE_ORIGIN = 'https://nectardocs.com'

// Numeric segment compare, so 0.10.0 sorts above 0.9.0 (a lexical compare puts
// it below, which would silently hide the newest release).
export function compareVersions(a, b) {
  const pa = String(a).split('.').map(Number)
  const pb = String(b).split('.').map(Number)
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] ?? 0) - (pb[i] ?? 0)
    if (d !== 0) return d
  }
  return 0
}

export function parseRelease(source, filename) {
  const { data, content } = matter(source)
  const where = `content/releases/${filename}`

  for (const field of ['version', 'date', 'headline']) {
    if (typeof data[field] !== 'string' || !data[field].trim()) {
      throw new Error(`${where}: frontmatter '${field}' is required and must be a non-empty string`)
    }
  }
  if (!Array.isArray(data.summary) || data.summary.length === 0) {
    throw new Error(`${where}: frontmatter 'summary' must be a non-empty array of strings`)
  }
  if (data.summary.some((s) => typeof s !== 'string' || !s.trim())) {
    throw new Error(`${where}: every 'summary' bullet must be a non-empty string`)
  }
  // The version is the routing key AND the app's gate. A filename that disagrees
  // publishes a page at one URL while the JSON points at another.
  if (filename !== `${data.version}.md`) {
    throw new Error(`${where}: filename must match the version — expected ${data.version}.md`)
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data.date)) {
    throw new Error(`${where}: 'date' must be YYYY-MM-DD`)
  }

  return {
    version: data.version,
    date: data.date,
    headline: data.headline,
    feature: data.feature === true,
    summary: data.summary,
    url: `${SITE_ORIGIN}/releases/${data.version}/`,
    embedUrl: `${SITE_ORIGIN}/releases/${data.version}/embed/`,
    // Raw HTML passes straight through — a release that needs a hand-built block
    // or a <video> can have one.
    bodyHtml: marked.parse(content, { async: false }),
  }
}

export function loadReleases(dir) {
  return readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => parseRelease(readFileSync(join(dir, f), 'utf8'), f))
    .sort((a, b) => compareVersions(b.version, a.version))
}

// The cross-repo contract. The app parses exactly this shape; the body never
// enters it.
export function whatsNewPayload(releases) {
  return {
    releases: [...releases]
      .sort((a, b) => compareVersions(b.version, a.version))
      .map(({ bodyHtml, ...rest }) => rest),
  }
}
