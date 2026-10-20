# sgit clone-headless, cli.sgit.ai

> Credentials-only clone: derive keys, write config, no data

*Source: <https://cli.sgit.ai/reference/clone-headless.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit clone-headless

Credentials-only clone: derive keys, write config, no data.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit clone-headless [options] <vault_key> [directory]
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key ({passphrase}:{vault_id}) |
| `directory` | optional | Cache directory (optional) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/clone-headless.html)*
