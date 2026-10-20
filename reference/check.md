# sgit check, cli.sgit.ai

> Vault integrity checks

*Source: <https://cli.sgit.ai/reference/check.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# sgit check

Vault integrity checks.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 3 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit check
```

## Subcommands

- [`sgit check fsck`](#check-fsck): Verify vault integrity and repair missing objects
- [`sgit check upload-objects`](#check-upload-objects): Upload specific local objects to the server (recovery tool — run on the vault that HAS the objects)
- [`sgit check verify`](#check-verify): Verify the ECDSA signature on every commit reachable from HEAD

### sgit check fsck {#check-fsck}

Verify vault integrity and repair missing objects

```text
sgit check fsck [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--repair` | Download missing objects from remote |
| `--verbose` | Show object type and referencing parent for each missing/corrupt object |

### sgit check upload-objects {#check-upload-objects}

Upload specific local objects to the server (recovery tool — run on the vault that HAS the objects)

```text
sgit check upload-objects [directory] <object_ids>
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |
| `object_ids` | required | Object IDs to upload (obj-cas-imm-...) |

### sgit check verify {#check-verify}

Verify the ECDSA signature on every commit reachable from HEAD

```text
sgit check verify [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--limit` | Stop after N commits (0 = all) |
| `--verbose` | List every commit with its status |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/check.html)*
