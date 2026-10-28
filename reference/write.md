# sgit write, cli.sgit.ai

> Write a file directly to vault HEAD (agent workflow)

*Source: <https://cli.sgit.ai/reference/write.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit write

Write a file directly to vault HEAD (agent workflow).

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit write [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | Vault-relative file path to write |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--also` | Additional files to include atomically (repeatable) |
| `--file` | Read content from LOCAL_FILE instead of stdin |
| `--json` | Print result as JSON instead of plain text |
| `--message` | Commit message (auto-generated if omitted) |
| `--push` | Push immediately after writing; stdout contains only the blob ID |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/write.html)*
