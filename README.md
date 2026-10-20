# SGit-AI__Website__Cli

The source of **https://cli.sgit.ai**, the documentation for the sgit command-line tool
(`pip install sgit-ai`): every command, generated from the CLI's own parser; the HTTP API it is a client
of; the guides; the CLI team's research, by topic; and articles in the newsroom's format. Part of the [sgit.ai](https://sgit.ai)
network. Started on 20 October 2026 from [a brief published in full](briefs/2026-10-20__cli-sgit-ai-first-brief.md).

Deployed by GitHub Pages on every push to `dev` (`.github/workflows/deploy-pages.yml`: validate, tag,
deploy), the same pipeline as [SGit-AI__Website](https://github.com/SGit-AI/SGit-AI__Website) and
[SGit-AI__Website__PKI](https://github.com/SGit-AI/SGit-AI__Website__PKI).

## Where things are

| Path | What it is |
|---|---|
| `admin/content/<path>.md` | the source of `<path>.html` and its markdown twin `<path>.md`; edit these, never the generated HTML |
| `admin/content/articles/<slug>.md` | one article in the newsroom's format; adding the file publishes it ([the contract](admin/content/articles/README.md)) |
| `admin/content/research/` | the CLI team's research documents, as written; `research/topics/` holds one file per research topic |
| `admin/content/reference/sgit-cli-reference.json` | `sgit help all --format json`; the command reference is generated from it |
| `REALITY.md` · `BRIEF-CORRECTIONS.md` | what exists, and where the brief was wrong; published as `admin/reality.html` and `admin/corrections.html` |
| `admin/build/build.py` | the generator: pages, twins, nav and footer, `llms.txt`, `llms-full.txt`, sitemap, `assets/version.js` |
| `admin/build/validate.js` | the gate: build current, version, links, canonical host, twins, orphans, key-leak tripwire |
| `admin/build/import_sgit_ai.py` | moves pages from sgit.ai (from its markdown twins) |
| `admin/build/import_cli_research.py` | publishes documents from the CLI repository in the research area |
| `admin/build/make_figures.py` | draws the articles' lead figures (`articles/images/`) |
| `admin/build/version.txt` | the site version |

Every other `.html`, `.md`, `llms*.txt` and `sitemap.xml` at the root and in `about/ admin/ api/ articles/
briefs/ docs/ reference/ research/ security/` is generated (listed in `admin/build/generated.json`).

## Release

1. Bump `admin/build/version.txt` and add a row to `admin/content/admin/versions.md`.
2. `python3 admin/build/build.py && node admin/build/validate.js`
3. `git commit -am "site vX.Y.Z: ..." && git push origin dev` (the `site vX.Y.Z:` prefix is what CI tags).
4. Check https://cli.sgit.ai/assets/version.js serves the new version.

## Updating the command reference for a new CLI release

```bash
pip install -U sgit-ai
sgit help all --format json -o admin/content/reference/sgit-cli-reference.json
sgit --help > admin/content/reference/sgit-help.txt
python3 admin/build/build.py && node admin/build/validate.js
```

Code Apache-2.0 (`LICENSE`); content CC BY 4.0.
