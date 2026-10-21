# Engineering, cli.sgit.ai

> How cli.sgit.ai is built, checked and released: one content folder, one generator, one gate, one version, deployed from dev by GitHub Pages; and how it measures against the estate's guidance for every sgit repository.

*Source: <https://cli.sgit.ai/admin/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Engineering: how this site is built and released

One folder of content, one generator, one gate, one version number. Deployed to https://cli.sgit.ai by GitHub Pages on every push to `dev`, the same pipeline as [sgit.ai](https://github.com/SGit-AI/SGit-AI__Website) and [pki.sgit.ai](https://github.com/SGit-AI/SGit-AI__Website__PKI).

## The shape

| Path | What it is |
|---|---|
| `admin/content/<path>.md` | the source of the page at `<path>.html`: flat front matter, then markdown |
| `admin/content/articles/<slug>.md` | one article in the newsroom's format; adding the file publishes it ([the contract](https://github.com/SGit-AI/SGit-AI__Website__Cli/blob/dev/admin/content/articles/README.md)) |
| `admin/content/research/<slug>.md` | one research document from the CLI repository, as written, with its topics |
| `admin/content/research/topics/<id>.md` | one research topic: the question, where it stands, and the `!topic` list of its documents and articles |
| `admin/content/reference/sgit-cli-reference.json` | the output of `sgit help all --format json`; the command reference is generated from it |
| `REALITY.md`, `BRIEF-CORRECTIONS.md` | at the repository root, published as [Reality](../admin/reality.md) and [Corrections](../admin/corrections.md) |
| `admin/build/build.py` | the generator: pages, markdown twins, nav and footer, `llms.txt`, `llms-full.txt`, sitemap, `assets/version.js` |
| `admin/build/md.py` | the markdown renderer, from pki.sgit.ai and newsroom.sgit.ai; escapes everything, so content cannot carry HTML |
| `admin/build/validate.js` | the gate |
| `admin/build/import_sgit_ai.py` | moves pages from sgit.ai, from their markdown twins ([what moved](../admin/moved.md)) |
| `admin/build/import_cli_research.py` | publishes documents from the CLI repository in the research area |
| `admin/build/make_figures.py` | draws the v0.2.0 articles' lead figures as SVG |
| `admin/build/render_figures.mjs`, `admin/build/figures/` | renders the drawn figures (one HTML page each) to webp, and every mermaid diagram in the content to SVG, with Playwright; run by hand, its output committed, so CI needs no browser |
| `admin/build/version.txt` | the site version, the one place it is written |
| `.github/workflows/deploy-pages.yml` | validate, tag, deploy |

Every generated file is listed in `admin/build/generated.json`, and the build deletes a listed file it no longer produces, so removing a content file removes its page and its twin.

## Releasing

1. Bump `admin/build/version.txt` and add a row to `admin/content/admin/versions.md` with one sentence on what changed and why. **Every release is a minor: the last number goes up by one** (v0.2.1, v0.2.2, v0.2.3). The middle number moves only when Dinis Cruz says so; this rule is his, from 20 October 2026. The tag job accepts exactly the next minor or a deliberate step of the middle number.
2. If a figure or a diagram changed, `node admin/build/render_figures.mjs`; then `python3 admin/build/build.py`
3. `node admin/build/validate.js`
4. `git commit -am "site vX.Y.Z: ..." && git push origin dev`. The `site vX.Y.Z:` prefix is load-bearing: the tag job finds the release commit by it and refuses a release whose newest prefix disagrees with `version.txt`.
5. Check that https://cli.sgit.ai/assets/version.js serves the new version. A clean push is not a release.

## The gate

`node admin/build/validate.js` fails the build on any of these, in CI on every push and pull request, before anything is tagged or deployed:

| Check | Why |
|---|---|
| The build is current (`build.py --check`) | a page edited by hand, or content committed without building, ships something the source does not say |
| The version agrees: `version.txt`, `assets/version.js`, `llms.txt`, one row in the release history | the badge on every page reads `version.js`; a release without its row has no record |
| Every internal link and asset resolves | an orphaned or misspelled link is a page nobody can reach |
| Every page has a canonical link on the CNAME host, and a markdown twin, and is in `llms.txt` | pages agents cannot read, or that claim to live elsewhere |
| No page is an orphan: every page is linked from another page | a page nothing links to is unpublished in practice |
| The leak tripwire: vault-key shapes, private-key markers, cloud and provider key prefixes, across every file | this site discusses keys constantly; it must never contain one |
| Every article is in the newsroom's format: its front matter, a summary of 220 to 360 words, In short, limits and sources, a lead figure that exists, no em-dash | the format is what lets the newsroom import an article unchanged ([the guidance](https://send.sgit.ai/articles/every-site-its-own-articles.html)) |
| A page left at a moved address points at a page that exists | the 21 research documents that were under /articles/ in v0.1 |
| Advisory, not failing: em-dashes in prose on this site's own pages | the estate's writing rule; pages moved or published verbatim, and research, keep their authors' punctuation |

## Against the estate's guidance

[Every sgit repository](https://sgit.ai/docs/guidance/repositories.html) lists what each repository carries. Where this one stands at v0.2.0:

| The guidance asks for | Here |
|---|---|
| The brief, published in full | [yes](../briefs/index.md), with the initial prompt |
| A reality file and a corrections file | [yes](../admin/reality.md), [yes](../admin/corrections.md) |
| One version, up on every push, shown on every page | yes: `version.txt`, the badge, the [release history](../admin/versions.md) |
| A gate that fails the build | yes, above |
| Machine-readable twins and `llms.txt` | yes, generated from the same source |
| Licences and a participant disclosure | yes: Apache-2.0 for code, CC BY 4.0 for content, [the disclosure](../about/participant.md) |
| Nav and footer injected at build | yes, from one definition in `build.py` |
| A credentials tier that is never committed | `.local/` is gitignored; nothing in this repository needs a secret to build |
| The review folder (`review/`) | **not yet**, recorded in [the reality file](../admin/reality.md) |
| Roles and a board, as files | **in part**: [the team](../about/team.md) names who writes; roles as files and a board are not yet here |
| A release script that verifies the live site | **not yet**: step 5 above is by hand |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/admin/index.html)*
