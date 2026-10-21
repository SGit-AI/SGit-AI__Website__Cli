#!/usr/bin/env node
// Renders the articles' drawn figures and diagrams. Run when a figure or a diagram changes, then commit
// what it writes; the build and the gate only check that the outputs exist, so CI needs no browser.
//
//   node admin/build/render_figures.mjs            render what is missing
//   node admin/build/render_figures.mjs --force    render everything again
//
// Two kinds of input, the newsroom's method for both (its admin/content/articles/README.md, "Figures"):
//
//   1. admin/build/figures/<name>.html: one small page per figure, in the site's colours from
//      figures/figures.css, 1,400 px wide. Rendered by Playwright's Chromium as a full-page screenshot and
//      converted to webp at quality 82 by Pillow: articles/images/<name>.webp. A figure is text that can be
//      corrected, not a picture that has to be redrawn.
//   2. ```mermaid fences in admin/content/**/*.md. Each is rendered once by mermaid in the same browser to
//      articles/images/mermaid/<sha256 of the source, 12 hex>.svg. The page shows the SVG, so no page loads a
//      script at read time; the markdown twin keeps the mermaid source, which agents and GitHub read as is.
//      Changing a diagram's source changes its name, so a stale diagram cannot be shown.
//
// Mermaid is loaded at render time only, pinned: MERMAID below.
import { createRequire } from 'module';
import { createHash } from 'crypto';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = createRequire('/opt/node22/lib/node_modules/')('playwright')); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const FIGS = path.join(ROOT, 'admin/build/figures');
const OUT = path.join(ROOT, 'articles/images');
const MOUT = path.join(OUT, 'mermaid');
const MERMAID = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js';
const FORCE = process.argv.includes('--force');

export const THEME = {
  theme: 'base', fontFamily: 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
  themeVariables: {
    background: '#faf9f5', primaryColor: '#e6f2f0', primaryBorderColor: '#0f766e', primaryTextColor: '#1c1d21',
    secondaryColor: '#fbefe3', secondaryBorderColor: '#b45309', tertiaryColor: '#f2f0e9', tertiaryBorderColor: '#d5d0c2',
    lineColor: '#5c5f66', textColor: '#1c1d21', fontSize: '15px', noteBkgColor: '#fbefe3', noteBorderColor: '#b45309',
    actorBkg: '#e6f2f0', actorBorder: '#0f766e', actorTextColor: '#1c1d21', signalColor: '#34363c', signalTextColor: '#1c1d21',
    labelBoxBkgColor: '#f2f0e9', labelBoxBorderColor: '#d5d0c2', loopTextColor: '#1c1d21', activationBkgColor: '#fbefe3',
    edgeLabelBackground: '#faf9f5', clusterBkg: '#f2f0e9', clusterBorder: '#d5d0c2',
  },
  flowchart: { htmlLabels: false, curve: 'basis', padding: 10, nodeSpacing: 34, rankSpacing: 38 },
  sequence: { mirrorActors: false, showSequenceNumbers: true },
};

export const hashOf = src => createHash('sha256').update(src).digest('hex').slice(0, 12);

function walk(dir, out = []) {
  for (const n of fs.readdirSync(dir)) {
    const p = path.join(dir, n);
    if (fs.statSync(p).isDirectory()) walk(p, out); else if (n.endsWith('.md')) out.push(p);
  }
  return out;
}

export function mermaidBlocks() {
  const blocks = [];
  for (const f of [...walk(path.join(ROOT, 'admin/content')), path.join(ROOT, 'REALITY.md'), path.join(ROOT, 'BRIEF-CORRECTIONS.md')]) {
    const lines = fs.readFileSync(f, 'utf8').split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim() !== '```mermaid') continue;
      const body = [];
      for (i++; i < lines.length && lines[i].trim() !== '```'; i++) body.push(lines[i]);
      const src = body.join('\n');
      blocks.push({ file: path.relative(ROOT, f), src, hash: hashOf(src) });
    }
  }
  return blocks;
}

async function main() {
  fs.mkdirSync(MOUT, { recursive: true });
  const browser = await chromium.launch();
  let figs = 0, diagrams = 0;

  for (const name of fs.readdirSync(FIGS).filter(n => n.endsWith('.html')).sort()) {
    const base = name.slice(0, -5), out = path.join(OUT, `${base}.webp`);
    if (!FORCE && fs.existsSync(out) && fs.statSync(out).mtimeMs > fs.statSync(path.join(FIGS, name)).mtimeMs
        && fs.statSync(out).mtimeMs > fs.statSync(path.join(FIGS, 'figures.css')).mtimeMs) continue;
    const page = await browser.newPage({ viewport: { width: 1400, height: 200 }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.join(FIGS, name));
    await page.waitForTimeout(200);
    const png = out.replace(/\.webp$/, '.png');
    await page.screenshot({ path: png, fullPage: true });
    await page.close();
    execFileSync('python3', ['-I', '-c', 'import sys; from PIL import Image; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], "WEBP", quality=82); import os; os.remove(sys.argv[1])', png, out]);
    figs++;
    console.log(`  · figure ${base}.webp`);
  }

  const blocks = mermaidBlocks();
  const todo = blocks.filter(b => FORCE || !fs.existsSync(path.join(MOUT, `${b.hash}.svg`)));
  if (todo.length) {
    const page = await browser.newPage();
    await page.setContent('<html><body></body></html>');
    await page.addScriptTag({ url: MERMAID });
    await page.evaluate(cfg => window.mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', ...cfg }), THEME);
    for (const b of todo) {
      const svg = await page.evaluate(async ([id, src]) => (await window.mermaid.render(id, src)).svg, [`m${b.hash}`, b.src]);
      // Shown through <img>, so the file must declare its namespace itself.
      fs.writeFileSync(path.join(MOUT, `${b.hash}.svg`), /^<svg[^>]*xmlns="/.test(svg) ? svg : svg.replace(/^<svg /, '<svg xmlns="http://www.w3.org/2000/svg" '));
      diagrams++;
      console.log(`  · diagram ${b.hash}.svg  (${b.file})`);
    }
    await page.close();
  }
  // Diagrams no content uses any more are removed, so the folder holds exactly what the pages show.
  const live = new Set(blocks.map(b => `${b.hash}.svg`));
  for (const n of fs.readdirSync(MOUT)) if (!live.has(n)) { fs.unlinkSync(path.join(MOUT, n)); console.log(`  · removed ${n}`); }
  await browser.close();
  console.log(`render_figures: ${figs} figure(s) and ${diagrams} diagram(s) rendered; ${blocks.length} diagrams in the content`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
