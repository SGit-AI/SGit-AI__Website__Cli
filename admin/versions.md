# Release history, cli.sgit.ai

> Every release of cli.sgit.ai, newest first, with one sentence on what changed and why.

*Source: <https://cli.sgit.ai/admin/versions.html> · generated from the same content as the page, so the two cannot drift.*

---
# Release history

The site's version is in `admin/build/version.txt` and goes up on every push to `dev`; the badge at the top of every page reads it. The command reference carries its own version, the sgit-ai release it was generated from.

| Version | Date | Command reference | What changed, and why |
|---|---|---|---|
| v0.2.3 | 2026-10-21 | sgit-ai v0.23.0 | Three fixes from reading the site on an iPad and an iPhone: every stylesheet and script is now asked for by a fingerprint of its contents, so a browser can no longer mix a cached v0.2.1 stylesheet with the new themes (which painted dark headings and grey text on Ember); the phone menu scrolls on its own instead of scrolling the page under it (the newsroom's fix); and the bar collapses behind Menu below 1,200px, where an iPad had wrapped it onto two rows. |
| v0.2.2 | 2026-10-21 | sgit-ai v0.23.0 | Five reading themes, the newsroom's: Newsprint, Night, Paper, Blueprint and Ember, chosen from a picker in the nav and remembered in the browser, with the system's dark setting as the default. Every colour in the stylesheet is now a token defined in all five, and the gate holds it so; figures and diagrams stay on light paper in every theme, as prints. |
| v0.2.1 | 2026-10-21 | sgit-ai v0.23.0 | The CLI team's pack-mode thread, made readable: [A pack per push](../articles/a-pack-per-push.md) as an article with two drawn figures and six flow diagrams; [a review of it with five decisions](../articles/pack-mode-read-closely.md) by the build agent; the spec and the brief to the SG/Send team under research; the zip article synced with its revised draft. Figures are now drawn the newsroom's way (an HTML page each, rendered to webp) and mermaid diagrams are rendered to SVG at authoring time. From here every release is a minor, at Dinis Cruz's instruction. |
| v0.2.0 | 2026-10-20 | sgit-ai v0.23.0 | Research and articles become two areas, from [the second brief](../briefs/2026-10-20__research-and-articles.md): 22 research documents as written under `/research/` in seven topics, each topic a question with what is shipped, designed and absent; ten articles under `/articles/` in the newsroom's format send.sgit.ai's guidance sets out, seven of them converted from the CLI team's drafts of 16 and 20 October, with lead figures; the gate holds articles to the format; the 21 v0.1 addresses send the reader on. A minor-version step because addresses moved. |
| v0.1.2 | 2026-10-20 | sgit-ai v0.23.0 | The reality file catches up: cli.sgit.ai was checked live after v0.1.1 deployed (DNS, Pages and the `dev` environment all work), so it moves from "does not exist yet" to "exists". |
| v0.1.1 | 2026-10-20 | sgit-ai v0.23.0 | The generator and the gate reach the repository: the Python `.gitignore` template's `build/` rule had kept `admin/build/` out of the v0.1.0 commit, so CI could not run `validate.js` and nothing deployed. `.gitignore` now re-includes `admin/build/`. |
| v0.1.0 | 2026-10-20 | sgit-ai v0.23.0 | The first version, built from [the brief](../briefs/index.md) the same day: 27 pages moved from sgit.ai (site v0.7.87) so the CLI's technical documentation has one home, the command reference generated from `sgit help all --format json` (158 commands), and 23 research documents from the CLI repository (`SGit-AI__CLI` at 5597526) published as articles, with the generator, the gate and the deploy pipeline the sibling sites run. |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/admin/versions.html)*
