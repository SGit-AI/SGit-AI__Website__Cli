---
title: What moved from sgit.ai
summary: The pages that moved from sgit.ai to cli.sgit.ai on 20 October 2026, each at the same path, and why: the CLI now has use cases of its own, and sgit.ai is the umbrella.
section: site
order: 3
---

# What moved from sgit.ai

On 20 October 2026 the CLI's most technical pages moved here from sgit.ai, as [the brief](/briefs/index.html) asks: the CLI now has a set of use cases of its own, and sgit.ai is the umbrella for the project and its commercial side. Each page kept its path, so `sgit.ai/docs/quickstart.html` is now `cli.sgit.ai/docs/quickstart.html`, and a redirect on sgit.ai is one rule.

The pages were taken from sgit.ai's markdown twins, which are generated from the same source as its HTML, at sgit.ai site v0.7.87, by `admin/build/import_sgit_ai.py`. The text is unchanged. Links to a page that moved now stay on this site; links to anything else go back to sgit.ai.

!moved

## What stayed on sgit.ai, and why

- **Vaults as a platform**: vault apps, `_page.json`, the browser bridge, sub-vaults, static hosting, publishing a vault, and the guidance for working on one. They are about the vault, not the command line.
- **The project**: why it exists, use cases, case studies, the published vaults, comparisons, the newsroom, partnerships.
- **The docs hub and the agent-contact protocol**, which serve the whole network.

## What sgit.ai still has to do

This site cannot change sgit.ai. Until sgit.ai's team acts, both copies exist, and **the copy here is the one maintained from now on**. The request to them, as recorded in [the corrections file](/admin/corrections.html):

1. Point each moved page at its new address: a link at the top, then a redirect.
2. Point sgit.ai's docs hub and `llms.txt` at cli.sgit.ai for the CLI.
3. Add cli.sgit.ai to the network directory (`admin/content/sites/cli.md`, the Cartographer's file).
