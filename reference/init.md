# sgit init, cli.sgit.ai

> Create a new empty vault and register it on the server

*Source: <https://cli.sgit.ai/reference/init.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# sgit init

Create a new empty vault and register it on the server.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit init [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Directory to create the vault in (default: current directory) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--existing` | Allow initialising into a non-empty directory without prompting |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--restore` | Restore vault from a .vault__*.zip backup in the target directory |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--vault-key` | Vault key ({passphrase}:{vault_id}). Generated randomly if omitted. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/init.html)*
