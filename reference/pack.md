# sgit pack, cli.sgit.ai

> Pack vaults: objects as zips on the host (import, export, compact, ls, verify, stats)

*Source: <https://cli.sgit.ai/reference/pack.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit pack

Pack vaults: objects as zips on the host (import, export, compact, ls, verify, stats).

*Generated from `sgit help all --format json`, sgit-ai v0.24.0. 6 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit pack [options]
```

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

## Subcommands

- [`sgit pack compact`](#pack-compact): One snapshot of the head; absorbed, superseded and orphan packs move to archive/
- [`sgit pack export`](#pack-export): Rewrite a pack-vault clone into a NEW normal vault (new key; source untouched)
- [`sgit pack import`](#pack-import): Rewrite a full clone of a normal vault into a NEW pack vault (new key; source untouched)
- [`sgit pack ls`](#pack-ls): List the packs on the host
- [`sgit pack stats`](#pack-stats): Packs and bytes on the host; local compression ratio
- [`sgit pack verify`](#pack-verify): Check every pack member against its content address

### sgit pack compact {#pack-compact}

One snapshot of the head; absorbed, superseded and orphan packs move to archive/

```text
sgit pack compact [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Pack-vault clone (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--dry-run` | Show the plan only |
| `--json` |  |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit pack export {#pack-export}

Rewrite a pack-vault clone into a NEW normal vault (new key; source untouched)

```text
sgit pack export [options] <source> <target>
```

| Argument | | What it is |
|---|---|---|
| `source` | required | Clone of the pack vault |
| `target` | required | Directory for the new normal vault |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` | Print the rewrite stats as JSON |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--vault-key` | Key for the new vault (generated if omitted) |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit pack import {#pack-import}

Rewrite a full clone of a normal vault into a NEW pack vault (new key; source untouched)

```text
sgit pack import [options] <source> <target>
```

| Argument | | What it is |
|---|---|---|
| `source` | required | Full clone of the normal vault |
| `target` | required | Directory for the new pack vault (must not exist as a vault) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` | Print the rewrite stats as JSON |
| `--no-deflate` | Packs without blob compression |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--vault-key` | Key for the new vault (generated if omitted) |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit pack ls {#pack-ls}

List the packs on the host

```text
sgit pack ls [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` |  |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit pack stats {#pack-stats}

Packs and bytes on the host; local compression ratio

```text
sgit pack stats [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` |  |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit pack verify {#pack-verify}

Check every pack member against its content address

```text
sgit pack verify [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` |  |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/pack.html)*
