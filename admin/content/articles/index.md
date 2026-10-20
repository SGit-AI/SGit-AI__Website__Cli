---
title: Research
summary: Articles from the sgit CLI team, newest first: measurements, designs, reviews, decisions and fixes, each taking one topic as far as the evidence goes, with its source in the CLI repository.
section: articles
hub: true
---

# Research

The CLI team's articles, newest first. Each takes **one topic, one implementation or one idea** as far as the evidence goes: a measurement on a real vault, a design and the review that corrected it, a bug traced to its cause. They are, in the words of [the brief](/briefs/index.html), "our new generation of briefs", and this is where they are captured first.

The first {{article_count}} were written in the CLI repository between 2 and 16 October 2026 (`team/humans/dinis_cruz/claude-code-web/`) and are published here as written, each with its source path and commit. The *kind* on each card says what it is worth: a **measurement** is numbers from a run; a **design**, **plan** or **analysis** is a proposal, not a shipped feature, unless it says so; a **fix** or **finding** names the code.

!list articles

## Publishing an article

Adding one file publishes it: `admin/content/articles/<slug>.md`, with a title, a date and a summary in its front matter. The contract is in `admin/content/articles/README.md`.
