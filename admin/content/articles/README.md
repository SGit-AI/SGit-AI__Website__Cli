# Publishing an article

*The authoring contract for `admin/content/articles/`. Since site v0.2.0 it is the newsroom's format, as
send.sgit.ai's [Every site its own articles](https://send.sgit.ai/articles/every-site-its-own-articles.html)
sets it out for every site in the network. Read that page first; this file is what is specific to here.*

## The one rule

> **Publishing is adding one file. Nothing else.**

`admin/content/articles/<slug>.md`, and its lead figure in `articles/images/`. The index, the home page's
list, the research topics that link it, the nav, `llms.txt` and the sitemap are derived by
`admin/build/build.py`. The slug is the address, and the address never changes once published.

## Article or research?

An **article** makes one argument for a reader, in the format below. A **research document** is the work
itself, published as written, under `admin/content/research/` and grouped into topics
(`admin/content/research/topics/`). If it is a record of work, it is research; if it is written to be read
start to finish as an argument, it is an article. When a research thread produces an argument, add the
article's slug to the topic's `articles:` list.

## The shape

```markdown
---
title: <hook>: <the argument in one line>
date: YYYY-MM-DD
time: HH:MM                             # optional, UTC: orders articles of the same day
author: Dinis Cruz                      # or cli.build, or another agent's <site>.<role>
author_url: https://sgit.ai/about/      # or https://cli.sgit.ai/about/team.html
summary: <220 to 360 words, first person, the whole argument with its numbers>
version: vX.Y.Z                         # the site release that publishes it
license: https://creativecommons.org/licenses/by/4.0/
tags: [<ten or so, kebab-case, the last one "article">]
status: published                       # or draft: written, held back from the build
---

!shot <slug>.svg | /articles/images/ | <the figure described in full, as sentences> | diagram

## In short {#in-short}
- **<the claim, in bold, as a sentence.>** <the number or the reason.>   (six to ten)

## <the argument, in sections with short anchors> {#anchor}

## What this does not claim {#limits}
- **<a limit.>** <why, and what would change it.>

If you <are in the reader's position>, write to agent@riskmandate.ai.

## Where this comes from {#sources}
<the origin; the responsibility line; every source, linked and dated; what the counts were made from>
```

The page's heading is the title; the byline, the summary and the tags are drawn from the front matter.

## Figures and diagrams

The newsroom's method (its `admin/content/articles/README.md`, "Figures"): a figure is the evidence, drawn,
two to six an article, where the evidence is.

- **A drawn figure** is one small page, `admin/build/figures/<prefix>-<name>.html`, using the shared
  `figures/figures.css` (the site's colours, a serif title, a one-paragraph reading, numbered boxes, dashed
  borders for what is proposed, a footer naming the source). `node admin/build/render_figures.mjs` renders it
  at 1,400 px to `articles/images/<prefix>-<name>.webp`. Place it with
  `!shot <prefix>-<name>.webp | /articles/images/ | <caption, two to four sentences> | <kind>`, kind one of
  `architecture`, `comparison`, `decision`, `diagram`, `timeline`, `playbook`.
- **A flow, a sequence or an architecture** can be a ```mermaid fence in the article. Its first line may be
  `%% <caption>`. The same command renders it to `articles/images/mermaid/<hash>.svg`; the page shows the SVG
  and loads no script, and the markdown twin keeps the mermaid source. Prefer top-down flowcharts: a wide one
  shrinks to unreadable text in the column.
- The v0.2.0 lead figures were drawn by `admin/build/make_figures.py` as SVG; that still works.
- Commit what the renderer writes. The build stops if a mermaid diagram has not been rendered.

## What the gate checks (`admin/build/validate.js`, check 9)

The front matter above, a summary of 220 to 360 words, tags as a list ending in `article`, the `{#in-short}`,
`{#limits}` and `{#sources}` sections, a `!shot` figure that exists, and no em-dash anywhere in the file.
The rest of the guidance's rules (British English, numbers counted by a script the article names, a status on
every claim, no absolutes, no praise, the memo's order kept, people named) are the writer's job; the gate
cannot read for them.

## The articles that started as CLI drafts

Seven articles were the CLI team's `article-draft__` documents (SGit-AI__CLI, `5473571`, branch
`claude/charming-babbage-5hzcxq`). They were converted once, by hand: the front matter, the summary, the
lead figure, the anchors, the contact line and Where this comes from were added, and the text kept as
drafted. They are maintained here from now on; a new draft in the CLI repository becomes an article by the
same conversion, not by re-importing.
