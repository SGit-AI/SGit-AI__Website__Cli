# sgit cat, cli.sgit.ai

> Decrypt and print a vault file to stdout

*Source: <https://cli.sgit.ai/reference/cat.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit cat

Decrypt and print a vault file to stdout.

*Generated from `sgit help all --format json`, sgit-ai v0.26.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit cat [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | File path inside the vault |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--id` | Print only the blob ID (zero network calls) |
| `--json` | Print file metadata as JSON (path, blob_id, size, content_type, fetched) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/cat.html)*
