// Pure parsing for release notes. Reads and validates; writes nothing.
// scripts/build-releases.mjs is the only thing that touches the filesystem.
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import matter from 'gray-matter'
import { marked } from 'marked'

export const SITE_ORIGIN = 'https://nectardocs.com'

// Announcements are published by TOPIC, not by version: /updates/data-rules,
// not /releases/0.6.0. The slug is the filename, so the URL is visible in the
// content directory and there is no second field to keep in sync. The version
// stays in frontmatter, where the desktop app reads it to decide whether the
// reader's build is new enough to be told about this at all.
const SLUG_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/

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
  const slug = filename.replace(/\.md$/, '')

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
  // The filename becomes a public URL, so it has to survive being one.
  if (!SLUG_RE.test(slug)) {
    throw new Error(`${where}: filename must be a lowercase hyphenated slug, e.g. data-rules.md`)
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data.date)) {
    throw new Error(`${where}: 'date' must be YYYY-MM-DD`)
  }

  return {
    slug,
    version: data.version,
    date: data.date,
    headline: data.headline,
    feature: data.feature === true,
    summary: data.summary,
    url: `${SITE_ORIGIN}/updates/${slug}/`,
    embedUrl: `${SITE_ORIGIN}/updates/${slug}/embed/`,
    // Raw HTML passes straight through — a release that needs a hand-built block
    // or a <video> can have one.
    bodyHtml: marked.parse(content, { async: false }),
  }
}

export function loadReleases(dir) {
  const releases = readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => parseRelease(readFileSync(join(dir, f), 'utf8'), f))
    .sort((a, b) => compareVersions(b.version, a.version))

  // Version is the app's gate, so two updates claiming the same one makes
  // "have they seen this" unanswerable. Slugs can't collide (they're filenames);
  // versions can, now that they're no longer the filename.
  const seen = new Set()
  for (const r of releases) {
    if (seen.has(r.version)) {
      throw new Error(`content/releases: two updates both claim version ${r.version}`)
    }
    seen.add(r.version)
  }
  return releases
}

// The cross-repo contract. The app parses exactly this shape; the body never
// enters it, and neither does the slug — the app follows the `url` and
// `embedUrl` we publish rather than assembling paths of its own, which is what
// let the route move from /releases/<version> to /updates/<slug> without the
// app changing at all.
export function whatsNewPayload(releases) {
  return {
    releases: [...releases]
      .sort((a, b) => compareVersions(b.version, a.version))
      .map(({ bodyHtml, slug, ...rest }) => rest),
  }
}
