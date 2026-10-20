# sgit branch, cli.sgit.ai

> Branch management

*Source: <https://cli.sgit.ai/reference/branch.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit branch

Branch management.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 7 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit branch
```

## Subcommands

- [`sgit branch checkout`](#branch-checkout): Switch to a branch or restore a specific commit
- [`sgit branch list`](#branch-list): List all named branches
- [`sgit branch merge`](#branch-merge): Merge another named branch into the current one
- [`sgit branch merge-abort`](#branch-merge-abort): Abort an in-progress merge
- [`sgit branch new`](#branch-new): Create a new named branch and switch to it
- [`sgit branch rename`](#branch-rename): Rename a branch this clone created and has not pushed
- [`sgit branch switch`](#branch-switch): Switch to a named branch

### sgit branch checkout {#branch-checkout}

Switch to a branch or restore a specific commit

```text
sgit branch checkout [options] [target] [directory]
```

| Argument | | What it is |
|---|---|---|
| `target` | optional | Branch name, branch ID, or commit ID to switch to |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--force` | Force checkout even if there are uncommitted changes (discards them) |
| `--vault-key` | Vault key (required for bare vaults without a saved key) |

### sgit branch list {#branch-list}

List all named branches

```text
sgit branch list [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit branch merge {#branch-merge}

Merge another named branch into the current one

```text
sgit branch merge [options] <name> [directory]
```

| Argument | | What it is |
|---|---|---|
| `name` | required | The branch to merge in (name or ID), e.g. feature or current |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL |
| `--token` | SG/Send access token |

### sgit branch merge-abort {#branch-merge-abort}

Abort an in-progress merge

```text
sgit branch merge-abort [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit branch new {#branch-new}

Create a new named branch and switch to it

```text
sgit branch new [options] <name> [directory]
```

| Argument | | What it is |
|---|---|---|
| `name` | required | New branch name |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--from` | Branch from a specific named branch (name or ID) |

### sgit branch rename {#branch-rename}

Rename a branch this clone created and has not pushed

```text
sgit branch rename [options] <old> <new> [directory]
```

| Argument | | What it is |
|---|---|---|
| `old` | required | Current branch name |
| `new` | required | New branch name |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL |
| `--token` | SG/Send access token |

### sgit branch switch {#branch-switch}

Switch to a named branch

```text
sgit branch switch [options] <name_or_id> [directory]
```

| Argument | | What it is |
|---|---|---|
| `name_or_id` | required | Named branch name or branch ID |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL |
| `--force` | Force switch even if there are uncommitted changes (discards them) |
| `--token` | SG/Send access token (to fetch the branch from the server) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/branch.html)*
