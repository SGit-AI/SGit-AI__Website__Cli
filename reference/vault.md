# sgit vault, cli.sgit.ai

> Vault management and credential store

*Source: <https://cli.sgit.ai/reference/vault.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit vault

Vault management and credential store.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. 41 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit vault
```

## Subcommands

- [`sgit vault add`](#vault-add): Store a vault key under an alias
- [`sgit vault attach`](#vault-attach): Bind a key to an existing .sg_vault/bare checkout (e.g. a fresh git clone of a one-repo vault)
- [`sgit vault backup`](#vault-backup): Create a backup zip of the vault
- [`sgit vault backups`](#vault-backups): List available backups for a vault
- [`sgit vault clean`](#vault-clean): Remove working copy, keeping bare vault; or prune empty dirs
- [`sgit vault delete-on-remote`](#vault-delete-on-remote): Hard-delete this vault from the server, keep local clone intact
- [`sgit vault derive-keys`](#vault-derive-keys): Derive vault_id / read_key / write_key / file ids from a vault key or {read_key}:{vault_id} (plumbing: bare hex output, accepts sgit_private_/sgit_public_ prefixes)
- [`sgit vault format`](#vault-format): Show or raise the vault format gate (object-id width, minimum client, features)
- [`sgit vault ignore`](#vault-ignore): Show always-ignored folders, or deliberately remove a now-ignored folder from the vault
- [`sgit vault info`](#vault-info): Show vault identity, remote, branch, and web URL
- [`sgit vault list`](#vault-list): List stored vault aliases
- [`sgit vault mirror`](#vault-mirror): Copy a published vault you cannot read (custody without access) — keyless, verifiable
- [`sgit vault move`](#vault-move): Move vault to a new identity (key rotation + optional server move)
- [`sgit vault rekey`](#vault-rekey): Replace the vault key and re-encrypt all content
- [`sgit vault rekey check`](#vault-rekey-check): Show vault state without making changes
- [`sgit vault rekey commit`](#vault-rekey-commit): Commit all files under the current key (run after init)
- [`sgit vault rekey init`](#vault-rekey-init): Re-initialise vault with a new key (run after wipe)
- [`sgit vault rekey wipe`](#vault-rekey-wipe): Wipe local encrypted store only (.sg_vault/ removed, files kept)
- [`sgit vault remote`](#vault-remote): Manage vault remotes
- [`sgit vault remote add`](#vault-remote-add): Add a remote
- [`sgit vault remote list`](#vault-remote-list): List configured remotes
- [`sgit vault remote remove`](#vault-remote-remove): Remove a remote
- [`sgit vault remote rename`](#vault-remote-rename): Rename a remote
- [`sgit vault remote set-default`](#vault-remote-set-default): Set the default remote
- [`sgit vault remote set-url`](#vault-remote-set-url): Update the URL of a remote
- [`sgit vault remote show`](#vault-remote-show): Show details of a remote
- [`sgit vault remove`](#vault-remove): Remove a stored vault key
- [`sgit vault restore`](#vault-restore): Restore a vault from a backup zip
- [`sgit vault serve`](#vault-serve): Moved: sgit serve --static
- [`sgit vault show`](#vault-show): Show vault key for an alias
- [`sgit vault show-key`](#vault-show-key): Show the vault key for the current directory
- [`sgit vault stash`](#vault-stash): Stash uncommitted changes
- [`sgit vault stash drop`](#vault-stash-drop): Drop last stash without applying
- [`sgit vault stash list`](#vault-stash-list): List stashes
- [`sgit vault stash pop`](#vault-stash-pop): Restore last stash
- [`sgit vault tag`](#vault-tag): Named, signed release pointers
- [`sgit vault tag create`](#vault-tag-create): Tag a pushed commit (default: this clone's head)
- [`sgit vault tag delete`](#vault-tag-delete): Delete a tag
- [`sgit vault tag list`](#vault-tag-list): List the tags
- [`sgit vault tag show`](#vault-tag-show): Show a tag and verify its signature
- [`sgit vault uninit`](#vault-uninit): Remove vault metadata (.sg_vault/), creating an auto-backup zip first

### sgit vault add {#vault-add}

Store a vault key under an alias

```text
sgit vault add [options] <alias>
```

| Argument | | What it is |
|---|---|---|
| `alias` | required | Human-friendly name for this vault |

| Option | What it does |
|---|---|
| `--vault-key` | Vault key (prompted if omitted) |

### sgit vault attach {#vault-attach}

Bind a key to an existing .sg_vault/bare checkout (e.g. a fresh git clone of a one-repo vault)

```text
sgit vault attach [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--read-key` | Read key (with --vault-id) -> read-only attach |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--vault-id` | Vault id, required with --read-key |
| `--vault-key` | Full vault key -> read-write attach |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit vault backup {#vault-backup}

Create a backup zip of the vault

```text
sgit vault backup [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--include-key` | Embed VAULT-KEY in the zip (opt-in; prompts unless --yes) |
| `--label` | Label suffix in the filename (default: manual) |
| `--output-dir` | Output directory (default: .sg_vault/backups/) |
| `--yes` | Skip confirmation prompts |

### sgit vault backups {#vault-backups}

List available backups for a vault

```text
sgit vault backups [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit vault clean {#vault-clean}

Remove working copy, keeping bare vault; or prune empty dirs

```text
sgit vault clean [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--empty-dirs` | Remove empty directories left after file deletions (normal vault) |

### sgit vault delete-on-remote {#vault-delete-on-remote}

Hard-delete this vault from the server, keep local clone intact

```text
sgit vault delete-on-remote [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--json` | Output result as JSON |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |
| `--yes` | Skip confirmation prompt |

### sgit vault derive-keys {#vault-derive-keys}

Derive vault_id / read_key / write_key / file ids from a vault key or {read_key}:{vault_id} (plumbing: bare hex output, accepts sgit_private_/sgit_public_ prefixes)

```text
sgit vault derive-keys <vault_key>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key ({passphrase}:{vault_id}), {read_key_hex}:{vault_id}, or either with its sgit_private_vault_/sgit_private_read_/sgit_public_read_ prefix |

### sgit vault format {#vault-format}

Show or raise the vault format gate (object-id width, minimum client, features)

```text
sgit vault format [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL |
| `--feature` | Add a feature flag (e.g. signatures-required); repeatable |
| `--min-client` | Refuse clients older than this version, by name |
| `--remove-feature` | Remove a feature flag; repeatable |
| `--set` | Raise the format: 2 = new objects get 128-bit (32-hex) ids; existing objects keep theirs, no move |
| `--token` | Access token |

### sgit vault ignore {#vault-ignore}

Show always-ignored folders, or deliberately remove a now-ignored folder from the vault

```text
sgit vault ignore [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--apply` | Remove tracked files under FOLDER from the vault in one visible commit; the work tree is untouched |
| `--yes` | Skip the confirmation prompt |

### sgit vault info {#vault-info}

Show vault identity, remote, branch, and web URL

```text
sgit vault info [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL |
| `--token` | Access token |

### sgit vault list {#vault-list}

List stored vault aliases

```text
sgit vault list
```

### sgit vault mirror {#vault-mirror}

Copy a published vault you cannot read (custody without access) — keyless, verifiable

```text
sgit vault mirror [options] [source] [dest]
```

| Argument | | What it is |
|---|---|---|
| `source` | optional | Published URL or folder to mirror from |
| `dest` | optional | Destination folder |

| Option | What it does |
|---|---|
| `--verify` | Re-check an existing mirror without fetching |

### sgit vault move {#vault-move}

Move vault to a new identity (key rotation + optional server move)

```text
sgit vault move [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--cleanup` | Finish or roll back a partially-completed move |
| `--dry-run` | Walk all 8 steps without any side effects |
| `--new-key` | New vault key (auto-generated if omitted) |
| `--reason` | Reason recorded in the sentinel commit |
| `--to` | Target API URL (same server if omitted) |
| `--token` | SG/Send access token |
| `--yes` | Skip all interactive prompts (CI / scripted use) |

### sgit vault rekey {#vault-rekey}

Replace the vault key and re-encrypt all content

```text
sgit vault rekey [options]
```

| Option | What it does |
|---|---|
| `--json` | Output result as JSON |
| `--new-key` | New vault key to use (generated if omitted) |
| `--yes` | Skip confirmation prompts |

#### sgit vault rekey check {#vault-rekey-check}

Show vault state without making changes

```text
sgit vault rekey check [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

#### sgit vault rekey commit {#vault-rekey-commit}

Commit all files under the current key (run after init)

```text
sgit vault rekey commit [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

#### sgit vault rekey init {#vault-rekey-init}

Re-initialise vault with a new key (run after wipe)

```text
sgit vault rekey init [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

| Option | What it does |
|---|---|
| `--new-key` | Key to use (generated if omitted) |

#### sgit vault rekey wipe {#vault-rekey-wipe}

Wipe local encrypted store only (.sg_vault/ removed, files kept)

```text
sgit vault rekey wipe [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional |  |

| Option | What it does |
|---|---|
| `--yes` | Skip confirmation prompt |

### sgit vault remote {#vault-remote}

Manage vault remotes

```text
sgit vault remote
```

#### sgit vault remote add {#vault-remote-add}

Add a remote

```text
sgit vault remote add [options] <name> <url> [remote_vault_id]
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name (e.g. origin) |
| `url` | required | Remote API URL |
| `remote_vault_id` | optional | Remote vault ID (defaults to current vault) |

| Option | What it does |
|---|---|
| `--default` | Set as the default remote |
| `--directory`, `-d` | Vault directory (default: .) |
| `--no-health-check` | Skip connectivity check on add |
| `--no-verify-tls` | Skip TLS certificate verification |

#### sgit vault remote list {#vault-remote-list}

List configured remotes

```text
sgit vault remote list [options]
```

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

#### sgit vault remote remove {#vault-remote-remove}

Remove a remote

```text
sgit vault remote remove [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name to remove |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

#### sgit vault remote rename {#vault-remote-rename}

Rename a remote

```text
sgit vault remote rename [options] <old_name> <new_name>
```

| Argument | | What it is |
|---|---|---|
| `old_name` | required | Current remote name |
| `new_name` | required | New remote name |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

#### sgit vault remote set-default {#vault-remote-set-default}

Set the default remote

```text
sgit vault remote set-default [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name to set as default |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

#### sgit vault remote set-url {#vault-remote-set-url}

Update the URL of a remote

```text
sgit vault remote set-url [options] <name> <new_url>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name |
| `new_url` | required | New API URL |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |
| `--no-health-check` | Skip connectivity check against the new URL |

#### sgit vault remote show {#vault-remote-show}

Show details of a remote

```text
sgit vault remote show [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

### sgit vault remove {#vault-remove}

Remove a stored vault key

```text
sgit vault remove <alias>
```

| Argument | | What it is |
|---|---|---|
| `alias` | required | Vault alias to remove |

### sgit vault restore {#vault-restore}

Restore a vault from a backup zip

```text
sgit vault restore [options] <source> <destination>
```

| Argument | | What it is |
|---|---|---|
| `source` | required | Backup zip path, or vault-dir:backup-id |
| `destination` | required | Target directory to restore into |

| Option | What it does |
|---|---|
| `--key` | Vault key (required for expanded if not in zip) |
| `--mode` | bare: vault only; expanded: vault + working copy (default: expanded) One of: `bare`, `expanded`. |
| `--verbose` | Print each file as it is written (vault objects and working copy) |
| `--yes` | Skip confirmation prompts |

### sgit vault serve {#vault-serve}

Moved: sgit serve --static

```text
sgit vault serve [rest]
```

| Argument | | What it is |
|---|---|---|
| `rest` | optional |  |

### sgit vault show {#vault-show}

Show vault key for an alias

```text
sgit vault show <alias>
```

| Argument | | What it is |
|---|---|---|
| `alias` | required | Vault alias |

### sgit vault show-key {#vault-show-key}

Show the vault key for the current directory

```text
sgit vault show-key [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit vault stash {#vault-stash}

Stash uncommitted changes

```text
sgit vault stash [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

#### sgit vault stash drop {#vault-stash-drop}

Drop last stash without applying

```text
sgit vault stash drop [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

#### sgit vault stash list {#vault-stash-list}

List stashes

```text
sgit vault stash list [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

#### sgit vault stash pop {#vault-stash-pop}

Restore last stash

```text
sgit vault stash pop [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit vault tag {#vault-tag}

Named, signed release pointers

```text
sgit vault tag [options]
```

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--directory` | ==SUPPRESS== |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

#### sgit vault tag create {#vault-tag-create}

Tag a pushed commit (default: this clone's head)

```text
sgit vault tag create [options] <name> [commit]
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Tag name, e.g. v1.0 or release/2026-10 |
| `commit` | optional | Commit id, short id or tag (default: HEAD) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--directory` | Vault directory (default: .) |
| `--force` | Re-point an existing tag on purpose |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |
| `-m`, `--message` | Tag message |

#### sgit vault tag delete {#vault-tag-delete}

Delete a tag

```text
sgit vault tag delete [options] <name> [directory]
```

| Argument | | What it is |
|---|---|---|
| `name` | required |  |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

#### sgit vault tag list {#vault-tag-list}

List the tags

```text
sgit vault tag list [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

#### sgit vault tag show {#vault-tag-show}

Show a tag and verify its signature

```text
sgit vault tag show [options] <name> [directory]
```

| Argument | | What it is |
|---|---|---|
| `name` | required |  |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

### sgit vault uninit {#vault-uninit}

Remove vault metadata (.sg_vault/), creating an auto-backup zip first

```text
sgit vault uninit [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/vault.html)*
