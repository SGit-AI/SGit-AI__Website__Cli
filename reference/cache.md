# sgit cache, cli.sgit.ai

> Declare cached paths (fast single-request reads)

*Source: <https://cli.sgit.ai/reference/cache.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# sgit cache

Declare cached paths (fast single-request reads).

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 4 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit cache
```

## Subcommands

- [`sgit cache add`](#cache-add): Declare a path as cached
- [`sgit cache repair`](#cache-repair): Reconcile cache objects with HEAD; drop orphans and duplicates
- [`sgit cache rm`](#cache-rm): Undeclare a cached path
- [`sgit cache status`](#cache-status): List cached paths and freshness

### sgit cache add {#cache-add}

Declare a path as cached

```text
sgit cache add [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | Vault-relative path (file or folder) |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--pointer` | Store a locator (blob_id/tree_id) instead of the value |
| `--value` | Store a copy of the file content (files only) |

### sgit cache repair {#cache-repair}

Reconcile cache objects with HEAD; drop orphans and duplicates

```text
sgit cache repair [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--dry-run` | Report what would change without changing anything |
| `--json` | Output as JSON |

### sgit cache rm {#cache-rm}

Undeclare a cached path

```text
sgit cache rm <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | Vault-relative path |
| `directory` | optional | Vault directory (default: .) |

### sgit cache status {#cache-status}

List cached paths and freshness

```text
sgit cache status [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--json` | Output as JSON |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/cache.html)*
