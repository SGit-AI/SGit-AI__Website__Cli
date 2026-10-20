# sgit history, cli.sgit.ai

> Commit history and diffs

*Source: <https://cli.sgit.ai/reference/history.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit history

Commit history and diffs.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 7 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit history
```

## Subcommands

- [`sgit history diff`](#history-diff): Show file-level and content-level diff
- [`sgit history log`](#history-log): Show commit history
- [`sgit history reflog`](#history-reflog): Where this clone's head has pointed (local, newest first)
- [`sgit history reset`](#history-reset): Reset local branch HEAD to a specific commit (git reset --hard)
- [`sgit history revert`](#history-revert): Restore working copy files to a past commit
- [`sgit history show`](#history-show): Show changes introduced by a commit
- [`sgit history undo`](#history-undo): Move this clone's head back to where it was before its last move (local)

### sgit history diff {#history-diff}

Show file-level and content-level diff

```text
sgit history diff [options] [range_spec] [directory]
```

| Argument | | What it is |
|---|---|---|
| `range_spec` | optional | Commit range (e.g. abc..def); synonym for --commit A --commit2 B |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--commit` | Compare working copy vs specific commit |
| `--commit2` | Second commit for commit-to-commit diff (requires --commit) |
| `--files-only` | Show file names only (no inline diff) |
| `--json` | Structured JSON output for agents |
| `--remote` | Compare working copy vs named branch HEAD |

### sgit history log {#history-log}

Show commit history

```text
sgit history log [options] [range_spec] [directory]
```

| Argument | | What it is |
|---|---|---|
| `range_spec` | optional | Commit range (e.g. abc..def); omit for full history |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--author` | Only commits by WHO: a branch name exactly (alice matches alice, not alice-laptop: use --author alice-laptop), or a signing key id / branch id, whole or by 4+ hex at either end (--author 3f9a) |
| `--file` | Show only commits that touched this file |
| `--files` | Include files changed per commit (range mode) |
| `--graph` | Show graph with connectors |
| `--grep` | Only commits whose message matches (case-insensitive regular expression) |
| `--json` | Structured JSON output for agents (range mode) |
| `--oneline` | Compact one-line-per-commit format |
| `--patch` | Include full diff per commit (range mode) |
| `--since` | Only commits at or after WHEN (2026-10-08, 2026-10-08T14:30, 3d, 12h, "2 weeks ago") |
| `--stat` | List the files each commit added (A), modified (M), deleted (D) or renamed (R) |
| `--until` | Only commits before WHEN (same forms) |
| `--vault-key` | Vault key (auto-read from .sg_vault/local/vault_key if omitted) |
| `-n`, `--max-count` | Limit output to the last N commits |

### sgit history reflog {#history-reflog}

Where this clone's head has pointed (local, newest first)

```text
sgit history reflog [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--all` | Every local ref, not just this clone's head |
| `-n`, `--max-count` | Show the last N moves (default 20, 0 = all) |

### sgit history reset {#history-reset}

Reset local branch HEAD to a specific commit (git reset --hard)

```text
sgit history reset [commit_id] [directory]
```

| Argument | | What it is |
|---|---|---|
| `commit_id` | optional | Target commit ID (full or prefix); omit to discard working-copy changes |
| `directory` | optional | Vault directory (default: .) |

### sgit history revert {#history-revert}

Restore working copy files to a past commit

```text
sgit history revert [options] [directory] [files]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |
| `files` | optional | Specific files to revert (default: all) |

| Option | What it does |
|---|---|
| `--as-commit` | Make a NEW commit that inverts --commit (git revert); push it to undo a pushed change for everyone |
| `--commit` | Revert to a specific commit (default: HEAD) |
| `--force` | Skip confirmation prompt when reverting all files |
| `-m`, `--message` | Message for --as-commit (default: Revert "<original>") |

### sgit history show {#history-show}

Show changes introduced by a commit

```text
sgit history show [options] <commit_id> [directory]
```

| Argument | | What it is |
|---|---|---|
| `commit_id` | required | Commit ID to inspect |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--files-only` | Show file names only (no inline diff) |

### sgit history undo {#history-undo}

Move this clone's head back to where it was before its last move (local)

```text
sgit history undo [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--force` | Undo even when the head is already on the server (this clone only) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/history.html)*
