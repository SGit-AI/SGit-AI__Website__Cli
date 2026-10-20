# sgit dev, cli.sgit.ai

> Dev/perf instrumentation tools (sgit dev <tool>)

*Source: <https://cli.sgit.ai/reference/dev.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit dev

Dev/perf instrumentation tools (sgit dev <tool>).

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 26 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit dev
```

## Subcommands

- [`sgit dev cat-object`](#dev-cat-object): Decrypt and display object contents
- [`sgit dev debug`](#dev-debug): Enable or disable debug mode for a vault
- [`sgit dev debug off`](#dev-debug-off): Disable debug mode
- [`sgit dev debug on`](#dev-debug-on): Enable debug mode
- [`sgit dev debug status`](#dev-debug-status): Show current debug mode state
- [`sgit dev derive-keys`](#dev-derive-keys): Derive and display vault keys
- [`sgit dev dump`](#dev-dump): Dump complete internal vault state as JSON
- [`sgit dev plugins`](#dev-plugins): Manage sgit-ai plugins
- [`sgit dev plugins disable`](#dev-plugins-disable): Disable a plugin
- [`sgit dev plugins enable`](#dev-plugins-enable): Enable a plugin
- [`sgit dev plugins list`](#dev-plugins-list): List all plugins with status
- [`sgit dev plugins show`](#dev-plugins-show): Show a plugin manifest
- [`sgit dev profile`](#dev-profile): Profile a vault operation
- [`sgit dev profile clone`](#dev-profile-clone): Profile the clone pipeline with per-phase timing
- [`sgit dev replay`](#dev-replay): Replay / diff a clone trace JSON offline
- [`sgit dev server-objects`](#dev-server-objects): Inventory remote objects by type
- [`sgit dev step-clone`](#dev-step-clone): Pausable clone with per-phase progress
- [`sgit dev tree-graph`](#dev-tree-graph): Visualise tree DAG from vault metadata
- [`sgit dev workflow`](#dev-workflow): Workflow framework tools (sgit dev workflow <cmd>)
- [`sgit dev workflow gc`](#dev-workflow-gc): Clean up old workflow workspaces
- [`sgit dev workflow inspect`](#dev-workflow-inspect): Inspect a workflow workspace by work-id
- [`sgit dev workflow list`](#dev-workflow-list): List registered workflows
- [`sgit dev workflow log`](#dev-workflow-log): Show recent transaction log records
- [`sgit dev workflow resume`](#dev-workflow-resume): Resume an interrupted workflow
- [`sgit dev workflow show`](#dev-workflow-show): Show steps + I/O schemas for a workflow
- [`sgit dev workflow trace`](#dev-workflow-trace): Pretty-print the SGIT_TRACE=1 step trace log

### sgit dev cat-object {#dev-cat-object}

Decrypt and display object contents

```text
sgit dev cat-object [options] <object_id>
```

| Argument | | What it is |
|---|---|---|
| `object_id` | required | Object ID (12-char hex) |

| Option | What it does |
|---|---|
| `--directory`, `-d` | Vault directory (default: .) |
| `--vault-key` | Vault key (auto-read from .sg_vault/local/vault_key if omitted) |

### sgit dev debug {#dev-debug}

Enable or disable debug mode for a vault

```text
sgit dev debug
```

#### sgit dev debug off {#dev-debug-off}

Disable debug mode

```text
sgit dev debug off [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

#### sgit dev debug on {#dev-debug-on}

Enable debug mode

```text
sgit dev debug on [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

#### sgit dev debug status {#dev-debug-status}

Show current debug mode state

```text
sgit dev debug status [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

### sgit dev derive-keys {#dev-derive-keys}

Derive and display vault keys

```text
sgit dev derive-keys <vault_key>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key ({passphrase}:{vault_id}) |

### sgit dev dump {#dev-dump}

Dump complete internal vault state as JSON

```text
sgit dev dump [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--output`, `-o` | Write dump JSON to FILE instead of stdout |
| `--remote` | Dump remote server state instead of local |
| `--structure-key` | Use structure key (hex) for metadata-only dump |

### sgit dev plugins {#dev-plugins}

Manage sgit-ai plugins

```text
sgit dev plugins
```

#### sgit dev plugins disable {#dev-plugins-disable}

Disable a plugin

```text
sgit dev plugins disable <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Plugin name |

#### sgit dev plugins enable {#dev-plugins-enable}

Enable a plugin

```text
sgit dev plugins enable <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Plugin name |

#### sgit dev plugins list {#dev-plugins-list}

List all plugins with status

```text
sgit dev plugins list [options]
```

| Option | What it does |
|---|---|
| `--json` | Output as JSON |

#### sgit dev plugins show {#dev-plugins-show}

Show a plugin manifest

```text
sgit dev plugins show <name>
```

| Argument | | What it is |
|---|---|---|
| `name` | required | Plugin name |

### sgit dev profile {#dev-profile}

Profile a vault operation

```text
sgit dev profile
```

#### sgit dev profile clone {#dev-profile-clone}

Profile the clone pipeline with per-phase timing

```text
sgit dev profile clone [options] <vault_key> <directory>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key ({passphrase}:{vault_id}) |
| `directory` | required | Directory to clone into |

| Option | What it does |
|---|---|
| `--json` | Output machine-readable JSON |
| `--output`, `-o` | Write JSON to FILE instead of stdout |
| `--sparse` | Sparse clone (no blob download) |

### sgit dev replay {#dev-replay}

Replay / diff a clone trace JSON offline

```text
sgit dev replay [options] <trace>
```

| Argument | | What it is |
|---|---|---|
| `trace` | required | Path to trace JSON (from sgit dev profile clone --json) |

| Option | What it does |
|---|---|
| `--diff` | Compare against a second trace JSON |
| `--json` | JSON output |

### sgit dev server-objects {#dev-server-objects}

Inventory remote objects by type

```text
sgit dev server-objects [options] <vault_key>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key |

| Option | What it does |
|---|---|
| `--json` | JSON output |
| `--output`, `-o` | Write JSON to FILE |

### sgit dev step-clone {#dev-step-clone}

Pausable clone with per-phase progress

```text
sgit dev step-clone [options] <vault_key> <directory>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key |
| `directory` | required | Directory to clone into |

| Option | What it does |
|---|---|
| `--json` | JSON output |
| `--no-pause` | Non-interactive; do not pause between steps |

### sgit dev tree-graph {#dev-tree-graph}

Visualise tree DAG from vault metadata

```text
sgit dev tree-graph [options] <vault_key>
```

| Argument | | What it is |
|---|---|---|
| `vault_key` | required | Vault key |

| Option | What it does |
|---|---|
| `--dot` | Write Graphviz DOT to FILE |
| `--json` | JSON output |
| `--output`, `-o` | Write JSON to FILE |

### sgit dev workflow {#dev-workflow}

Workflow framework tools (sgit dev workflow <cmd>)

```text
sgit dev workflow
```

#### sgit dev workflow gc {#dev-workflow-gc}

Clean up old workflow workspaces

```text
sgit dev workflow gc [options]
```

| Option | What it does |
|---|---|
| `--older-than` | Remove workspaces older than N days (default: 7) |
| `--vault-dir`, `-d` | Vault directory (default: .) |

#### sgit dev workflow inspect {#dev-workflow-inspect}

Inspect a workflow workspace by work-id

```text
sgit dev workflow inspect [options] <work_id>
```

| Argument | | What it is |
|---|---|---|
| `work_id` | required | Work ID (or prefix) |

| Option | What it does |
|---|---|
| `--vault-dir`, `-d` | Vault directory (default: .) |

#### sgit dev workflow list {#dev-workflow-list}

List registered workflows

```text
sgit dev workflow list
```

#### sgit dev workflow log {#dev-workflow-log}

Show recent transaction log records

```text
sgit dev workflow log [options]
```

| Option | What it does |
|---|---|
| `--filter` | Filter by workflow name |
| `--vault-dir`, `-d` | Vault directory (default: .) |

#### sgit dev workflow resume {#dev-workflow-resume}

Resume an interrupted workflow

```text
sgit dev workflow resume [options] <work_id>
```

| Argument | | What it is |
|---|---|---|
| `work_id` | required | Work ID to resume |

| Option | What it does |
|---|---|
| `--vault-dir`, `-d` | Vault directory (default: .) |

#### sgit dev workflow show {#dev-workflow-show}

Show steps + I/O schemas for a workflow

```text
sgit dev workflow show <workflow>
```

| Argument | | What it is |
|---|---|---|
| `workflow` | required | Workflow name (e.g. clone) |

#### sgit dev workflow trace {#dev-workflow-trace}

Pretty-print the SGIT_TRACE=1 step trace log

```text
sgit dev workflow trace [options] [vault_dir]
```

| Argument | | What it is |
|---|---|---|
| `vault_dir` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--filter` | Filter by workflow name |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/dev.html)*
