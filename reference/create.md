# sgit create, cli.sgit.ai

> Create a new vault and push it to the server in one step

*Source: <https://cli.sgit.ai/reference/create.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit create

Create a new vault and push it to the server in one step.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit create [options] <vault_name>
```

| Argument | | What it is |
|---|---|---|
| `vault_name` | required | Vault name / directory to create |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-push` | Initialise locally but skip the initial push |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--packs` | Create a pack vault (see sgit init --packs) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--vault-key` | Vault key ({passphrase}:{vault_id}). Auto-generated if omitted. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/create.html)*
