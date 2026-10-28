# sgit push, cli.sgit.ai

> Push clone branch to the named branch

*Source: <https://cli.sgit.ai/reference/push.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit push

Push clone branch to the named branch.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit push [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--branch-only` | Push clone branch objects and ref without updating named branch |
| `--force` | Overwrite remote ref unconditionally (no CAS check). Use after sgit history reset <commit> to rewind a branch. |
| `--force-with-lease` | Force, but only if the remote branch is still where this clone last saw it (or at COMMIT); refuses, writing nothing, if a teammate pushed since. |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/push.html)*
