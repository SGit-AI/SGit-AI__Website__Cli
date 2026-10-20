---
title: Research
summary: The sgit CLI team's research, kept as written and grouped into topics: measurements on real vaults, designs and the reviews that corrected them, security reviews, and the bugs found in daily use, each with its source in the CLI repository.
section: research
hub: true
---

# Research

The CLI team's working documents, **published as written**: measurements on real vaults, designs and the reviews that corrected them, decisions, security reviews and the bugs found in daily use. Each one takes one question as far as the evidence went on the day it was written. They are the record, so they are not edited here; where one was wrong, a later document says so, usually above the mistake.

**Research is not the same as an article.** An [article](/articles/index.html) makes one argument for a reader, in the newsroom's format, and is written to be read start to finish. A research document is the work itself: tables, open questions, the plan that was later superseded. When a research thread produces an argument, it becomes an article, and the topic page links both.

## Topics

Each topic is one open question, with where it stands today: what is shipped, what is designed, what is absent.

!list topics

## Every document, newest first

!list research

## Where these come from

The CLI repository, `team/humans/dinis_cruz/claude-code-web/MM/DD/`, written by the CLI team's agents (Claude Code sessions) for Dinis Cruz between 2 and 20 October 2026. `admin/build/import_cli_research.py` copies them here with a front matter and nothing else; each page names its source file, commit and branch. This import was taken from commit `5473571` on the CLI's working branch `claude/charming-babbage-5hzcxq`, which holds everything on `dev` plus the documents of 16 and 20 October that were not yet merged when they were published here.
