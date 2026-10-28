# sgit pull, cli.sgit.ai

> Pull named branch changes and merge into clone branch

*Source: <https://cli.sgit.ai/reference/pull.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit pull

Pull named branch changes and merge into clone branch.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit pull [options] [directory]
```

| Argument | | What it is |
|---|---|---|
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--accept-rewind` | Take a remote named branch that was rewound or rewritten (after a deliberate sgit push --force) |
| `--base-url` | API base URL (overrides --remote, global --base-url, and saved config) |
| `--conflict` | Conflict markers in lines style: merge (ours, theirs; the default) or diff3 (ours, the common version, theirs) One of: `diff3`, `merge`. |
| `--merge` | Files both sides changed: files keeps yours and writes theirs to <file>.conflict (the default), lines merges them line by line as git does, with conflict markers where they collide (also: SGIT_MERGE_STYLE) One of: `files`, `lines`. |
| `--no-checkout` | Selective working copy only: move the head and list what changed, write no file (sgit checkout --since-pull writes it) |
| `--no-verify-tls` | Skip TLS certificate verification (staging / self-signed only) |
| `--remote` | Use the named remote (URL + tls_verify from saved config); overrides the default remote for this command |
| `--token` | SG/Send access token (overrides global --token and saved config) |
| `--transport` | How to reach the vault: auto (default — a folder is local, an http(s) host is api unless its batch endpoint is absent), api (live SG/API), static (any GET host, read-only), local (a folder, read-only) One of: `api`, `auto`, `local`, `static`. |
| `--verify-tls` | Verify TLS certificates (default) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/pull.html)*
