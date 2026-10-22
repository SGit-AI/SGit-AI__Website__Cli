# sgit publish, cli.sgit.ai

> Generate the plaintext surface for static publishing (.sg_vault/publish/ — the only path that changes)

*Source: <https://cli.sgit.ai/reference/publish.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit publish

Generate the plaintext surface for static publishing (.sg_vault/publish/ — the only path that changes).

*Generated from `sgit help all --format json`, sgit-ai v0.24.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit publish [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--api-docs` | Emit api/docs/ (Swagger UI); implies --api-spec. Default mode: cdn (SRI-pinned); bundled vendors ~1.53 MB One of: `bundled`, `cdn`. |
| `--api-spec` | Emit api/openapi.json describing this folder (a few KB) |
| `--bundles` | Also emit bundles/ (head snapshot + per-commit delta zips) |
| `--layout` | URL layout recorded in the manifest (default: api-path) One of: `api-path`, `flat`. |
| `--visibility` | bare (default): no key published, unlisted; public: the READ KEY is published in the folder — irreversible One of: `bare`, `named`, `public`. |
| `--yes` | Skip confirmation prompts (CI use) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/publish.html)*
