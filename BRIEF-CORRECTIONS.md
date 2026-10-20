---
title: Corrections
summary: Where the brief was wrong or unclear, what was found, and what was done instead. The brief itself is never edited.
section: site
order: 5
---

# Corrections to the brief

The brief is [published as given](/briefs/index.html). Where it was wrong, unclear or overtaken, the finding goes here, dated, newest first, and the brief stays as it was.

## 2026-10-20, while building v0.1.0

1. **The names in the transcript are transcription errors.** "cli.sketo.ai" is `cli.sgit.ai` (the repository's README says so); "Escrip. AI" and "sk.ai" are `sgit.ai`; "the Skit" is sgit. Read throughout as such.
2. **"The API website for the CLI" is read as the CLI's documentation, with the HTTP API in it.** The brief goes on to describe a documentation site, so the site is that; the HTTP API pages moved here too, because the CLI is a client of that API and nothing else documents it as a whole.
3. **"Move" cannot be finished from this repository.** The pages are copied here and marked as moved, but sgit.ai still serves them and does not point here. Until sgit.ai's team adds links and redirects, both copies exist, and the one here is maintained from now on. The request is on [What moved](/admin/moved.html).
4. **"The most technical and the most detailed" needed a line drawn.** Drawn at: pages about the command-line tool, its keys, its protocol and its operation moved; pages about vaults as a platform (vault apps, `_page.json`, the browser bridge, publishing) stayed, since they are about the vault rather than the CLI. Twenty-seven pages moved.
5. **"The articles in the CLI repository" were not articles yet.** Two are article drafts for the newsroom; the rest are research notes, designs, reviews, measurements and fix write-ups for Dinis. Twenty-three of the October documents, those that take one topic as far as it goes, are published as articles, with a *kind* that says which of these each is. Replies to other teams and per-commit review responses were left in the CLI repository.
6. **The guidance "at sgit.ai for how to set up these websites" is two pages.** [Every sgit repository](https://sgit.ai/docs/guidance/repositories.html) and the vault guidance. The sibling sites (pki.sgit.ai, sgit.ai itself) supplied the pipeline. Where this site does not yet meet the guidance (the review folder, roles and a board, a release script that checks the live site), it is said on [the engineering page](/admin/index.html) and in [the reality file](/admin/reality.html).
7. **One difference from the sibling sites, chosen on purpose.** pki.sgit.ai's pages are hand-written HTML with the chrome injected; here every page is generated from markdown, because most of this site's content arrives as markdown (sgit.ai's twins, the CLI repository's documents, the CLI's own reference) and converting it by hand would be the drift the guidance warns about.
