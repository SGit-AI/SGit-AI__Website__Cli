# Command reference, cli.sgit.ai

> Every sgit command, subcommand, argument and option, generated from the CLI's own parser (sgit help all --format json), grouped by what it is for.

*Source: <https://cli.sgit.ai/reference/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Command reference

All **177 commands** of **sgit-ai v0.26.8**, generated from the parser the CLI actually builds. The CLI walks its own argparse tree (`CLI__Reference`, behind `sgit help all --format json`, schema `sgit-cli-reference-v1`); this site renders that JSON and nothing else. A flag cannot appear here unless the code registers it, and none the code registers can be missing.

- The same data, as published: [sgit-cli-reference.json](../reference/sgit-cli-reference.json). Diff two releases' files to see exactly what changed.
- Your installed version, offline: `sgit help all`, or `sgit help <command>`.
- Global options go before the command: `sgit [--base-url URL] [--token TOKEN] [--vault PATH] [--debug] <command> ...`.

Where to put a new command is a rule of the CLI (its `CLAUDE.md`): a daily-use verb at the top level, anything about the vault as a whole under `vault`, anything about commits under `history`, checks under `check`.

### Daily work

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit clone`](../reference/clone.md) |  | Clone a vault from the remote server |
| [`sgit init`](../reference/init.md) |  | Create a new empty vault and register it on the server |
| [`sgit create`](../reference/create.md) |  | Create a new vault and push it to the server in one step |
| [`sgit status`](../reference/status.md) |  | Show uncommitted changes in working directory |
| [`sgit commit`](../reference/commit.md) |  | Commit local changes to the clone branch |
| [`sgit pull`](../reference/pull.md) |  | Pull named branch changes and merge into clone branch |
| [`sgit push`](../reference/push.md) |  | Push clone branch to the named branch |
| [`sgit fetch`](../reference/fetch.md) |  | Fetch file content on demand (sparse clone) |
| [`sgit write`](../reference/write.md) |  | Write a file directly to vault HEAD (agent workflow) |
| [`sgit cat`](../reference/cat.md) |  | Decrypt and print a vault file to stdout |
| [`sgit ls`](../reference/ls.md) |  | List vault files with fetch status |
| [`sgit file`](../reference/file.md) | 4 | File operations (cat, ls, write, grep) |
| [`sgit publish`](../reference/publish.md) |  | Generate the plaintext surface for static publishing (.sg_vault/publish/ — the only path that changes) |

### Branches and merges

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit branch`](../reference/branch.md) | 7 | Branch management |
| [`sgit merge-abort`](../reference/merge-abort.md) |  | Abort an in-progress merge and restore working tree |
| [`sgit resolve`](../reference/resolve.md) |  | Resolve merge conflicts per file or all at once |

### History

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit history`](../reference/history.md) | 8 | Commit history and diffs |

### The vault as a whole

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit vault`](../reference/vault.md) | 41 | Vault management and credential store |
| [`sgit remote`](../reference/remote.md) | 7 | Manage vault remotes (alias for `sgit vault remote`) |
| [`sgit migrate`](../reference/migrate.md) | 3 | Run vault data migrations |
| [`sgit cache`](../reference/cache.md) | 4 | Declare cached paths (fast single-request reads) |

### Keys and identity

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit pki`](../reference/pki.md) | 10 | PKI key management and encryption |

### Checking and looking inside

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit check`](../reference/check.md) | 3 | Vault integrity checks |
| [`sgit inspect`](../reference/inspect.md) | 6 | Read-only vault inspection tools |
| [`sgit doctor`](../reference/doctor.md) |  | Check remote connectivity and configuration |

### Running a vault locally

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit serve`](../reference/serve.md) | 8 | Run this vault on your machine: the vault UI + API in a container (Docker, Podman, Apple container), or --static |

### Other ways to clone

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit clone-branch`](../reference/clone-branch.md) |  | Thin clone: full commit history + HEAD trees/blobs only. Note: only HEAD is fully fetched — run 'sgit fetch <path>' or 'sgit pull' to access older history. |
| [`sgit clone-headless`](../reference/clone-headless.md) |  | Credentials-only clone: derive keys, write config, no data |
| [`sgit clone-range`](../reference/clone-range.md) |  | Clone a specific commit range (range_from..range_to) |

### The tool itself

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit help`](../reference/help.md) |  | Show help (use `sgit help all` for full surface) |
| [`sgit version`](../reference/version.md) |  | Show sgit-ai version |
| [`sgit update`](../reference/update.md) |  | Update sgit-ai to the newest build (X.Y.0 is a release, X.Y.N a dev build) |

### For developers of sgit

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit dev`](../reference/dev.md) | 26 | Dev/perf instrumentation tools (sgit dev <tool>) |

### Not yet grouped

| Command | Subcommands | What it does |
|---|---|---|
| [`sgit checkout`](../reference/checkout.md) |  | Write tracked files into a selective working copy (a clone made with --no-checkout or --sparse); sgit branch checkout <target> switches branches |
| [`sgit grep`](../reference/grep.md) |  | Search the files of the working copy or a revision, as git grep |
| [`sgit pack`](../reference/pack.md) | 14 | Pack vaults: objects as zips on the host (import, export, compact, ls, verify, stats) |

## How this page is made

`admin/content/reference/sgit-cli-reference.json` is the output of `sgit help all --format json` from the release named above, installed from PyPI. The build turns it into one page per top-level command. To update: install the new release, run the command into that file, rebuild, and say in the release history which version the reference moved to.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/index.html)*
