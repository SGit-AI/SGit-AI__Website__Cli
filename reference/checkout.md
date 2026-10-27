# sgit checkout, cli.sgit.ai

> Write tracked files into a selective working copy (a clone made with --no-checkout or --sparse); sgit branch checkout <target> switches branches

*Source: <https://cli.sgit.ai/reference/checkout.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit checkout

Write tracked files into a selective working copy (a clone made with --no-checkout or --sparse); sgit branch checkout <target> switches branches.

*Generated from `sgit help all --format json`, sgit-ai v0.26.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit checkout [options] [paths]
```

| Argument | | What it is |
|---|---|---|
| `paths` | optional | Files or folders to write (a folder means everything under it) |

| Option | What it does |
|---|---|
| `--all` | Write every tracked file; the clone becomes a full one |
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--changed-since` | Write what changed between COMMIT and HEAD |
| `--directory` | Vault directory (default: .) |
| `--force` | Overwrite uncommitted edits at the paths written (by default they are kept) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--since-pull` | Write what the last pull added or changed |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/checkout.html)*
