# sgit file, cli.sgit.ai

> File operations (cat, ls, write)

*Source: <https://cli.sgit.ai/reference/file.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit file

File operations (cat, ls, write).

*Generated from `sgit help all --format json`, sgit-ai v0.24.0. 3 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit file
```

## Subcommands

- [`sgit file cat`](#file-cat): Decrypt and print a vault file to stdout
- [`sgit file ls`](#file-ls): List vault files with fetch status
- [`sgit file write`](#file-write): Write a file directly to vault HEAD (agent/programmatic workflow)

### sgit file cat {#file-cat}

Decrypt and print a vault file to stdout

```text
sgit file cat [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | File path inside the vault |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--id` | Print only the blob ID (zero network calls) |
| `--json` | Print file metadata as JSON (path, blob_id, size, content_type, fetched) |

### sgit file ls {#file-ls}

List vault files with fetch status

```text
sgit file ls [options] [path] [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | optional | Subdirectory or file path (default: root) |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--ids` | Include blob IDs in output |
| `--json` | Output full entry metadata as JSON array |

### sgit file write {#file-write}

Write a file directly to vault HEAD (agent/programmatic workflow)

```text
sgit file write [options] <path> [directory]
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

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/file.html)*
