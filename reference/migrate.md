# sgit migrate, cli.sgit.ai

> Run vault data migrations

*Source: <https://cli.sgit.ai/reference/migrate.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit migrate

Run vault data migrations.

*Generated from `sgit help all --format json`, sgit-ai v0.25.0. 3 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit migrate
```

## Subcommands

- [`sgit migrate apply`](#migrate-apply): Apply pending migrations
- [`sgit migrate plan`](#migrate-plan): Show pending migrations
- [`sgit migrate status`](#migrate-status): Show applied migrations

### sgit migrate apply {#migrate-apply}

Apply pending migrations

```text
sgit migrate apply [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--force` | Rewrite history even though the vault has signed commits (other clones will need sgit pull --accept-rewind) |

### sgit migrate plan {#migrate-plan}

Show pending migrations

```text
sgit migrate plan [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit migrate status {#migrate-status}

Show applied migrations

```text
sgit migrate status [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/migrate.html)*
