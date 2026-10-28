# sgit commit, cli.sgit.ai

> Commit local changes to the clone branch

*Source: <https://cli.sgit.ai/reference/commit.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit commit

Commit local changes to the clone branch.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit commit [options] [positionals]
```

| Argument | | What it is |
|---|---|---|
| `positionals` | optional | Without -m: the commit message (auto-generated if omitted). With -m: paths to commit (only those; every other change stays uncommitted). Paths also go after --: sgit commit "msg" -- a.txt docs/ "*.md" |

| Option | What it does |
|---|---|
| `--allow-deletions` | In sparse clones, allow files absent from disk to be deleted (default: preserve unfetched entries) |
| `--allow-secret-file` | Commit PATH although it looks like a vault secret (a zip with a key file in it); names one file, repeatable |
| `--amend` | Replace the last commit (not yet pushed) with the working copy and/or a new -m message |
| `--hunk` | Commit only this hunk (id from --list-hunks); repeatable. The working copy is not changed |
| `--json` | Print one JSON object (committed / nothing_to_commit / refused) |
| `--list-hunks` | Print the hunks of the changed files (or the named paths) with their ids; commits nothing |
| `--split` | With --list-hunks: list each change of a splittable hunk on its own |
| `-d`, `--directory` | Vault directory (default: .) |
| `-m`, `--message` | Commit message via flag (git-style); positionals are then paths. |
| `-p`, `--patch` | Choose hunks interactively (needs a terminal; agents use --list-hunks / --hunk) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/commit.html)*
