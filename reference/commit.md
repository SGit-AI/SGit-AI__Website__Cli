# sgit commit, cli.sgit.ai

> Commit local changes to the clone branch

*Source: <https://cli.sgit.ai/reference/commit.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# sgit commit

Commit local changes to the clone branch.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit commit [options] [message]
```

| Argument | | What it is |
|---|---|---|
| `message` | optional | Commit message (auto-generated if omitted) |

| Option | What it does |
|---|---|
| `--allow-deletions` | In sparse clones, allow files absent from disk to be deleted (default: preserve unfetched entries) |
| `--allow-secret-file` | Commit PATH although it looks like a vault secret (a zip with a key file in it); names one file, repeatable |
| `--amend` | Replace the last commit (not yet pushed) with the working copy and/or a new -m message |
| `-d`, `--directory` | Vault directory (default: .) |
| `-m`, `--message` | Commit message via flag (git-style). Overrides the positional arg. |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/commit.html)*
