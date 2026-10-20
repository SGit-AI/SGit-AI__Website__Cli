# sgit serve, cli.sgit.ai

> Run this vault on your machine: the vault UI + API in a container (Docker, Podman, Apple container), or --static

*Source: <https://cli.sgit.ai/reference/serve.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit serve

Run this vault on your machine: the vault UI + API in a container (Docker, Podman, Apple container), or --static.

*Generated from `sgit help all --format json`, sgit-ai v0.23.0. 8 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit serve [options]
```

| Option | What it does |
|---|---|
| `--bind` | Address to bind (default 127.0.0.1; 0.0.0.0 exposes it to your network) |
| `--data` | Data folder for the server (default: .sg_vault/serve/data in this clone) |
| `--image` | Image to run (default diniscruz/sg-send-vault:latest) |
| `--no-pull` | Do not check for a newer image; use the one already here |
| `--open` | Open the UI in a browser |
| `--port` | Port on this machine (default 8420; the next free one if taken) |
| `--runtime` | container \| docker \| podman \| nerdctl \| finch \| uv (default: the first found) |
| `--static` | Read-only server for a published vault (default: this vault's .sg_vault/publish/, publishing first if needed) |
| `--ui-dir` | Built vault UI folder (uv engine only) |

## Subcommands

- [`sgit serve install`](#serve-install): Install a container runtime (shows what, then asks)
- [`sgit serve logs`](#serve-logs): Server output
- [`sgit serve pull`](#serve-pull): Bring work done in the browser into this clone (fast-forward)
- [`sgit serve push`](#serve-push): Send this clone's commits to the local server
- [`sgit serve runtimes`](#serve-runtimes): Container runtimes on this machine
- [`sgit serve status`](#serve-status): Is it running, where, which image
- [`sgit serve stop`](#serve-stop): Stop the local server
- [`sgit serve update`](#serve-update): Get the newest image and restart (same data)

### sgit serve install {#serve-install}

Install a container runtime (shows what, then asks)

```text
sgit serve install [options] [runtime]
```

| Argument | | What it is |
|---|---|---|
| `runtime` | optional | container \| podman \| docker \| uv (default: the one recommended here) |

| Option | What it does |
|---|---|
| `--yes` | Do not ask |

### sgit serve logs {#serve-logs}

Server output

```text
sgit serve logs [options]
```

| Option | What it does |
|---|---|
| `-f`, `--follow` |  |

### sgit serve pull {#serve-pull}

Bring work done in the browser into this clone (fast-forward)

```text
sgit serve pull
```

### sgit serve push {#serve-push}

Send this clone's commits to the local server

```text
sgit serve push [options]
```

| Option | What it does |
|---|---|
| `--force` | Overwrite commits that exist only on the local server |

### sgit serve runtimes {#serve-runtimes}

Container runtimes on this machine

```text
sgit serve runtimes
```

### sgit serve status {#serve-status}

Is it running, where, which image

```text
sgit serve status
```

### sgit serve stop {#serve-stop}

Stop the local server

```text
sgit serve stop
```

### sgit serve update {#serve-update}

Get the newest image and restart (same data)

```text
sgit serve update
```

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/serve.html)*
