# sgit inspect, cli.sgit.ai

> Read-only vault inspection tools

*Source: <https://cli.sgit.ai/reference/inspect.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit inspect

Read-only vault inspection tools.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. 6 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit inspect
```

## Subcommands

- [`sgit inspect diff-state`](#inspect-diff-state): Compare two vault dumps and report divergences
- [`sgit inspect ignored`](#inspect-ignored): Audit what is excluded from vault tracking
- [`sgit inspect object`](#inspect-object): Show object details
- [`sgit inspect stats`](#inspect-stats): Show object store statistics
- [`sgit inspect tree`](#inspect-tree): Show current tree entries
- [`sgit inspect vault`](#inspect-vault): Show vault state overview

### sgit inspect diff-state {#inspect-diff-state}

Compare two vault dumps and report divergences

```text
sgit inspect diff-state [options] [dump_a] [dump_b] [directory]
```

| Argument | | What it is |
|---|---|---|
| `dump_a` | optional | Path to first dump JSON file |
| `dump_b` | optional | Path to second dump JSON file |
| `directory` | optional | Vault directory for on-the-fly dump (default: .) |

| Option | What it does |
|---|---|
| `--local` | Produce local dump on the fly |
| `--remote` | Produce remote dump on the fly |

### sgit inspect ignored {#inspect-ignored}

Audit what is excluded from vault tracking

```text
sgit inspect ignored [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--rules` | Print the curated ignore sets (no filesystem walk) |
| `--why` | Explain whether and why <path> is ignored or tracked |

### sgit inspect object {#inspect-object}

Show object details

```text
sgit inspect object <object_id> [directory]
```

| Argument | | What it is |
|---|---|---|
| `object_id` | required | Object ID (12-char hex) |
| `directory` | optional | Vault directory (default: .) |

### sgit inspect stats {#inspect-stats}

Show object store statistics

```text
sgit inspect stats [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit inspect tree {#inspect-tree}

Show current tree entries

```text
sgit inspect tree [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--vault-key` | Vault key (auto-read from .sg_vault/local/vault_key if omitted) |

### sgit inspect vault {#inspect-vault}

Show vault state overview

```text
sgit inspect vault [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/inspect.html)*
