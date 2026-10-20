# sgit remote, cli.sgit.ai

> Manage vault remotes (alias for `sgit vault remote`)

*Source: <https://cli.sgit.ai/reference/remote.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# sgit remote

Manage vault remotes (alias for `sgit vault remote`).

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 7 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit remote
```

## Subcommands

- [`sgit remote add`](#remote-add): Add a remote
- [`sgit remote list`](#remote-list): List configured remotes
- [`sgit remote remove`](#remote-remove): Remove a remote
- [`sgit remote rename`](#remote-rename): Rename a remote
- [`sgit remote set-default`](#remote-set-default): Set the default remote
- [`sgit remote set-url`](#remote-set-url): Update the URL of a remote
- [`sgit remote show`](#remote-show): Show details of a remote

### sgit remote add {#remote-add}

Add a remote

```text
sgit remote add [options] <name> <url> [remote_vault_id]
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

### sgit remote list {#remote-list}

List configured remotes

```text
sgit remote list [options]
```

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

### sgit remote remove {#remote-remove}

Remove a remote

```text
sgit remote remove [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name to remove |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

### sgit remote rename {#remote-rename}

Rename a remote

```text
sgit remote rename [options] <old_name> <new_name>
```

| Argument | | What it is |
|---|---|---|
| `old_name` | required | Current remote name |
| `new_name` | required | New remote name |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

### sgit remote set-default {#remote-set-default}

Set the default remote

```text
sgit remote set-default [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name to set as default |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

### sgit remote set-url {#remote-set-url}

Update the URL of a remote

```text
sgit remote set-url [options] <name> <new_url>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name |
| `new_url` | required | New API URL |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |
| `--no-health-check` | Skip connectivity check against the new URL |

### sgit remote show {#remote-show}

Show details of a remote

```text
sgit remote show [options] <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Remote name |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/remote.html)*
