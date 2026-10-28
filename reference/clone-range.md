# sgit clone-range, cli.sgit.ai

> Clone a specific commit range (range_from..range_to)

*Source: <https://cli.sgit.ai/reference/clone-range.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit clone-range

Clone a specific commit range (range_from..range_to).

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit clone-range [options] <vault_key> <range> [directory]
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key ({passphrase}:{vault_id}) |
| `range` | required | Commit range (e.g. abc123..def456) |
| `directory` | optional | Directory to clone into (default: vault ID) |

| Option | What it does |
|---|---|
| `--bare` | No working-copy extraction (structure only) |
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/clone-range.html)*
