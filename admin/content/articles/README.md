# Publishing an article

*The authoring contract for `admin/content/articles/`, adopted from sgit.ai's (`admin/content/CONTENT.md`),
whose central rule is the one worth copying.*

## The one rule

> **Publishing is adding one file. Nothing else.**

No index to update, no HTML to write, no menu to edit. The research index, the home page's latest list, the
nav, `llms.txt`, `llms-full.txt` and the sitemap are all derived at build time by `admin/build/build.py`.
Two agents publishing on the same day touch two different files and cannot conflict.

## The file

`admin/content/articles/<slug>.md`. The slug is the permalink (`/articles/<slug>.html`) and must not change
once published, because somebody may already have shared it.

```markdown
---
title: What the article finds, as a sentence
date: 2026-10-20                 # required, YYYY-MM-DD
time: 14:05                      # optional, UTC: orders articles published the same day
kind: measurement                # measurement · design · analysis · plan · decision · review · fix · finding · position · research · case study · roadmap
tags: clone, performance         # comma-separated, shown as chips
summary: One or two sentences. Required: it is the card text and the meta description.
author: who wrote it
source: https://github.com/SGit-AI/SGit-AI__CLI/blob/<commit>/<path>   # when it was written elsewhere first
source_path: <path>
source_commit: <short commit>
status: published                # or: draft (written, held back from the build)
---

# The title again, as the page's heading

The body, in the markdown admin/build/md.py renders.
```

## Rules

1. **Say what it is worth.** The `kind` is not decoration: a design is not a feature, a plan is not a
   result. If the article proposes something that does not exist, it says so in its first paragraph.
2. **Source every number.** A figure names the run, the vault or the file it came from.
3. **Links inside the site are root-relative**: `/reference/clone.html`, never `../reference/clone.html`.
4. **Corrections go above the mistake**, dated, with the mistake left visible, as the CLI team's documents
   already do ("Revised 2026-10-10 after the sgit.ai agent's review").
5. **Run the build before committing**: `python3 admin/build/build.py` then `node admin/build/validate.js`.

## Articles that started in the CLI repository

`admin/build/import_cli_research.py --cli <clone>` copies the documents listed in its `ARTICLES` table from
`team/humans/dinis_cruz/claude-code-web/` into this folder, adding the front matter and nothing else. Add a
row there and re-run it to publish another one; re-running takes the current version of every listed
document.
