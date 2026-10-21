#!/usr/bin/env node
// cli.sgit.ai pre-release gate. Run from anywhere: node admin/build/validate.js
// Ported from pki.sgit.ai's, with the checks this site's shape adds. Checks, in order:
//   1. the build is current — admin/build/build.py --check: every page, twin and index is what the content
//      produces now, so a hand-edited page or content committed without building cannot ship
//   2. version agreement — admin/build/version.txt vs assets/version.js, llms.txt, and exactly one row for
//      it in the release history
//   3. internal links — every relative href/src in every .html file resolves to a file in the tree
//   4. canonical host — every canonical and og:url points at the host in CNAME; every page declares one
//   5. twins and the index — every page has its .md twin and appears in llms.txt
//   6. orphans — every page except the home page is linked from at least one other page
//   7. key-leak tripwire — nothing in the tree may look like a vault key, a private key, or a cloud or
//      provider API key. The site discusses keys constantly; it must never contain one.
//   8. advisory: em-dashes in the prose of this site's own pages (not the moved or published-verbatim ones)
//   9. articles in the newsroom's format (send.sgit.ai, "Every site its own articles"): the front matter it
//      lists, a summary of 220 to 360 words, tags ending in "article", the In short, limits and sources
//      anchors, a lead figure that exists, and no em-dash anywhere. Research is published as written and is
//      not held to this, on purpose.
// Pages left at a moved address (meta sgit:moved-to) are checked for one thing: that where they send exists.
// Any failure exits 1: no tag, no publish.
'use strict';
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const errors = [];
const advisories = [];
const rel = f => path.relative(ROOT, f).split(path.sep).join('/');

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    if (['.git', 'node_modules', '.sg_vault', '.local'].includes(name)) continue;
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

const files = walk(ROOT);
const isStub = f => /<meta name="sgit:moved-to"/.test(fs.readFileSync(f, 'utf8'));
const stubs = files.filter(f => f.endsWith('.html') && isStub(f));
// admin/build/figures/ holds the sources render_figures.mjs draws the articles' figures from: inputs, not pages.
const isFigureSource = f => rel(f).startsWith('admin/build/figures/');
const htmlFiles = files.filter(f => f.endsWith('.html') && !stubs.includes(f) && !isFigureSource(f));
for (const f of stubs) {
  const to = fs.readFileSync(f, 'utf8').match(/<meta name="sgit:moved-to" content="([^"]+)"/)[1];
  if (!fs.existsSync(path.join(ROOT, to))) errors.push(`${rel(f)}: moved to ${to}, which does not exist`);
}

// --- 1. the build is current ---------------------------------------------
{
  const r = spawnSync('python3', [path.join(ROOT, 'admin/build/build.py'), '--check'], { encoding: 'utf8' });
  if (r.status !== 0) errors.push((r.stderr || r.stdout || 'build.py --check failed').trim());
}

// --- 2. version agreement -------------------------------------------------
const VERSION = fs.readFileSync(path.join(ROOT, 'admin/build/version.txt'), 'utf8').trim();
if (!/^v\d+\.\d+\.\d+$/.test(VERSION)) errors.push(`version.txt does not carry a vX.Y.Z version: "${VERSION}"`);
const VJS = path.join(ROOT, 'assets/version.js');
if (!fs.existsSync(VJS) || !fs.readFileSync(VJS, 'utf8').includes(`"${VERSION}"`)) {
  errors.push(`assets/version.js does not carry ${VERSION} (run admin/build/build.py)`);
}
const llms = fs.readFileSync(path.join(ROOT, 'llms.txt'), 'utf8');
if (!llms.includes(`Site version: ${VERSION}`)) errors.push(`llms.txt does not say Site version: ${VERSION}`);
const versions = fs.readFileSync(path.join(ROOT, 'admin/content/admin/versions.md'), 'utf8');
const rows = [...versions.matchAll(/^\| (v\d+\.\d+\.\d+) \|/gm)].map(m => m[1]);
if (!rows.includes(VERSION)) errors.push(`admin/content/admin/versions.md has no row for ${VERSION}`);
for (const v of new Set(rows)) if (rows.filter(x => x === v).length > 1) errors.push(`the release history lists ${v} more than once`);
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  if (/<nav class="site">/.test(t) && !/assets\/version\.js/.test(t)) {
    errors.push(`${rel(f)}: no assets/version.js — its version badge would be empty forever`);
  }
}

// --- 3. internal links ----------------------------------------------------
const linkedFrom = new Map();
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  const dir = path.dirname(f);
  for (const m of t.matchAll(/(?:href|src)="([^"#]*)(?:#[^"]*)?"/g)) {
    const target = m[1];
    if (/^(https?:|mailto:|data:|\/\/)/.test(target) || target === '') continue;
    const filePart = target.split('?')[0];
    const abs = path.resolve(dir, filePart);
    if (!fs.existsSync(abs)) { errors.push(`${rel(f)}: broken link -> ${target}`); continue; }
    if (abs !== f) {
      if (!linkedFrom.has(abs)) linkedFrom.set(abs, new Set());
      linkedFrom.get(abs).add(f);
    }
  }
}

// --- 4. canonical host ----------------------------------------------------
const HOST = fs.readFileSync(path.join(ROOT, 'CNAME'), 'utf8').trim();
if (!/^[a-z0-9.-]+$/.test(HOST)) errors.push(`CNAME does not carry a hostname: "${HOST}"`);
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  const claimed = [
    ...[...t.matchAll(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"/g)].map(m => m[1]),
    ...[...t.matchAll(/<meta[^>]+property="og:url"[^>]+content="([^"]+)"/g)].map(m => m[1]),
  ];
  for (const url of claimed) if (url !== `https://${HOST}/${rel(f)}`) {
    errors.push(`${rel(f)}: canonical/og:url is not this page on ${HOST} -> ${url}`);
  }
  if (!/rel="canonical"/.test(t)) errors.push(`${rel(f)}: no canonical link`);
}

// --- 5. twins and the index -----------------------------------------------
for (const f of htmlFiles) {
  const twin = f.slice(0, -5) + '.md';
  if (!fs.existsSync(twin)) errors.push(`${rel(f)}: no markdown twin`);
  if (!llms.includes(`(/${rel(twin)})`)) errors.push(`${rel(f)}: not in llms.txt`);
}

// --- 6. orphans -----------------------------------------------------------
// The nav and the footer link every section, so a page reachable only from them still counts: what this
// catches is a page nothing links to at all, which is unpublished in practice.
for (const f of htmlFiles) {
  if (rel(f) === 'index.html') continue;
  if (!linkedFrom.has(f)) errors.push(`${rel(f)}: orphan — no other page links to it`);
}

// --- 7. key-leak tripwire -------------------------------------------------
const SHAPES = [
  ['a vault key', /[A-Za-z0-9_-]{20,}:[0-9a-z]{8}(?:-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})?\b/],
  ['a private key', /-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----/],
  ['an AWS access key id', /\bAKIA[0-9A-Z]{16}\b/],
  ['a GitHub token', /\bgh[pousr]_[A-Za-z0-9]{36,}\b/],
  ['an OpenRouter / OpenAI-style key', /\bsk-(?:or-v1-|proj-)?[A-Za-z0-9]{32,}\b/],
  ['an Anthropic key', /\bsk-ant-[A-Za-z0-9_-]{20,}\b/],
];
// Shapes that look like a vault key and are not one: placeholders the docs teach with.
const ALLOWED = [/<[^>]*passphrase[^>]*>:/i, /x{20,}:/i, /passphrase-goes-here/i];
for (const f of files) {
  if (/\.(png|jpg|jpeg|gif|webp|ico|woff2?|zip|pdf)$/.test(f)) continue;
  if (rel(f) === 'admin/build/validate.js') continue;
  const t = fs.readFileSync(f, 'utf8');
  for (const [what, rx] of SHAPES) {
    const g = new RegExp(rx.source, 'g');
    for (const m of t.matchAll(g)) {
      const around = t.slice(Math.max(0, m.index - 40), m.index + m[0].length + 10);
      if (ALLOWED.some(a => a.test(around))) continue;
      errors.push(`${rel(f)}: contains ${what}-shaped string near "${m[0].slice(0, 12)}…"`);
      break;
    }
  }
}

// --- 8. advisory: em-dashes in this site's own prose -----------------------
for (const f of walk(path.join(ROOT, 'admin/content'))) {
  if (!f.endsWith('.md') || /\/(articles|research)\/(?!index\.md|README\.md)/.test(f)) continue;
  const t = fs.readFileSync(f, 'utf8');
  if (/^moved_from:/m.test(t)) continue;
  const prose = t.replace(/```[\s\S]*?```/g, '').replace(/`[^`]*`/g, '');
  const n = (prose.match(/—/g) || []).length;
  if (n) advisories.push(`${rel(f)}: ${n} em-dash(es) in prose`);
}

// --- 9. articles in the newsroom's format ------------------------------------
{
  const dir = path.join(ROOT, 'admin/content/articles');
  const REQUIRED = ['title', 'date', 'author', 'author_url', 'summary', 'version', 'license', 'tags', 'status'];
  for (const name of fs.readdirSync(dir)) {
    if (!name.endsWith('.md') || name === 'index.md' || name === 'README.md') continue;
    const where = `admin/content/articles/${name}`;
    const t = fs.readFileSync(path.join(dir, name), 'utf8');
    const fm = (t.match(/^---\n([\s\S]*?)\n---/) || [, ''])[1];
    const meta = Object.fromEntries(fm.split('\n').filter(l => l.includes(':')).map(l => [l.slice(0, l.indexOf(':')).trim(), l.slice(l.indexOf(':') + 1).trim()]));
    for (const k of REQUIRED) if (!meta[k]) errors.push(`${where}: no ${k} in the front matter`);
    if (meta.status === 'draft') continue;
    const words = (meta.summary || '').split(/\s+/).filter(Boolean).length;
    if (words < 220 || words > 360) errors.push(`${where}: the summary is ${words} words; the format asks for 220 to 360`);
    if (!/^\[.*,\s*article\]$/.test(meta.tags || '')) errors.push(`${where}: tags must be a [list] whose last tag is "article"`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(meta.date || '')) errors.push(`${where}: date is not YYYY-MM-DD`);
    for (const a of ['in-short', 'limits', 'sources']) if (!t.includes(`{#${a}}`)) errors.push(`${where}: no {#${a}} section`);
    const shot = t.match(/^!shot\s+([^|]+?)\s*\|\s*([^|]+?)\s*\|/m);
    if (!shot) errors.push(`${where}: no lead figure (!shot FILE | DIR | CAPTION)`);
    else if (!fs.existsSync(path.join(ROOT, shot[2].replace(/^\//, ''), shot[1]))) errors.push(`${where}: the lead figure ${shot[2]}${shot[1]} does not exist`);
    const dashes = (t.match(/\u2014/g) || []).length;
    if (dashes) errors.push(`${where}: ${dashes} em-dash(es); the format has none`);
  }
}

// --- report ---------------------------------------------------------------
for (const a of advisories) console.log('  · advisory: ' + a);
if (errors.length) {
  console.error(`validate: ${errors.length} error(s)`);
  for (const e of errors) console.error('  ✗ ' + e);
  process.exit(1);
}
console.log(`validate: OK — ${VERSION} on ${HOST}, ${htmlFiles.length} pages, build current, links resolve, ` +
            `twins and llms.txt complete, no orphans, no key-shaped strings`);
