# sgit clone, cli.sgit.ai

> Clone a vault from the remote server

*Source: <https://cli.sgit.ai/reference/clone.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit clone

Clone a vault from the remote server.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit clone [options] <vault_key> [directory]
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key — one of: {passphrase}:{vault_id} (full clone), {read_key_hex}:{vault_id} (auto-detects read-only), or just {vault_id} when --read-key is set; - reads it from stdin (keeps it out of argv and history) |
| `directory` | optional | Directory to clone into (default: vault ID) |

| Option | What it does |
|---|---|
| `--bare` | Clone vault structure only — no working-copy files extracted (full implementation in B09; currently stubs) |
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--depth` | Shallow clone: fetch only the newest N commits of history (1 = HEAD only). Commit, push and pull work normally; history commands stop at the boundary (sgit fetch --unshallow). |
| `--force` | Delete existing directory and re-clone from scratch |
| `--no-checkout` | Selective working copy: the vault's objects and index, no file written; sgit checkout <path> / --since-pull writes what you need (on a pack vault every object is already local, so a checkout is a local write) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--pack-store` | Pack vault: keep the packs in place and read objects from them by offset instead of extracting every object into bare/data/ (sgit pack store status \| extract \| rebuild) |
| `--path` | Scoped clone: hold only this vault folder (repeatable). Other folders are carried by id and never downloaded; commits and pulls touch only the held folders. Widen later with sgit fetch <folder>. |
| `--read-key` | Read-only clone using a 64-hex AES-256 read key. When set, the positional vault_key is the vault_id only (no passphrase prefix). Equivalent shorthand: pass "<HEX>:<vault_id>" as the positional. |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--sparse` | Download only structure (commits + trees); fetch file content on demand |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/clone.html)*
