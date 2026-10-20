# sgit fetch, cli.sgit.ai

> Fetch file content on demand (sparse clone)

*Source: <https://cli.sgit.ai/reference/fetch.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit fetch

Fetch file content on demand (sparse clone).

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit fetch [options] [path] [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | optional | File or directory path to fetch (default: all) |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--all` | Fetch all unfetched files (convert sparse clone to full) |
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--unshallow` | Shallow clone: fetch the history behind the boundary commit(s) |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/fetch.html)*
