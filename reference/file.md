# sgit file, cli.sgit.ai

> File operations (cat, ls, write, grep)

*Source: <https://cli.sgit.ai/reference/file.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit file

File operations (cat, ls, write, grep).

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. 4 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit file
```

## Subcommands

- [`sgit file cat`](#file-cat): Decrypt and print a vault file to stdout
- [`sgit file grep`](#file-grep): Search file contents, as git grep
- [`sgit file ls`](#file-ls): List vault files with fetch status
- [`sgit file write`](#file-write): Write a file directly to vault HEAD (agent/programmatic workflow)

### sgit file cat {#file-cat}

Decrypt and print a vault file to stdout

```text
sgit file cat [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | File path inside the vault |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--id` | Print only the blob ID (zero network calls) |
| `--json` | Print file metadata as JSON (path, blob_id, size, content_type, fetched) |

### sgit file grep {#file-grep}

Search file contents, as git grep

```text
sgit file grep [options] [positionals]
```

| Argument | | What it is |
|---|---|---|
| `positionals` | optional | The pattern (unless -e), then revisions to search instead of the working copy; paths go after -- |

| Option | What it does |
|---|---|
| `--json` | One JSON object (grep_v1) |
| `--offline` | Never fetch a blob this clone does not hold |
| `--text`, `-a` | Search binary files as text |
| `--untracked` | Also search untracked files |
| `-A` | N lines after each match |
| `-B` | N lines before each match |
| `-C` | N lines around each match |
| `-E`, `--extended-regexp` | Accepted: patterns are Python regexes |
| `-F`, `--fixed-strings` | The pattern is a literal string |
| `-H` | Print file names (the default) |
| `-I` | Do not search binary files |
| `-L`, `--files-without-match` | Print only the files that do not |
| `-P`, `--perl-regexp` | Accepted: patterns are Python regexes |
| `-c`, `--count` | Print path:count |
| `-d`, `--directory` | Vault directory (default: .) |
| `-e` | A pattern (repeatable: lines matching any) |
| `-h` | Do not print file names |
| `-i`, `--ignore-case` | Ignore case |
| `-l`, `--files-with-matches` | Print only the files that match |
| `-m`, `--max-count` | Stop after N matching lines per file |
| `-n`, `--line-number` | Prefix line numbers |
| `-o`, `--only-matching` | Print only the matched parts |
| `-q`, `--quiet` | Print nothing; the exit code tells |
| `-v`, `--invert-match` | Lines that do not match |
| `-w`, `--word-regexp` | Match whole words |

### sgit file ls {#file-ls}

List vault files with fetch status

```text
sgit file ls [options] [path] [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | optional | Subdirectory or file path (default: root) |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--ids` | Include blob IDs in output |
| `--json` | Output full entry metadata as JSON array |

### sgit file write {#file-write}

Write a file directly to vault HEAD (agent/programmatic workflow)

```text
sgit file write [options] <path> [directory]
```

| Argument | | What it is |
|---|---|---|
| `path` | required | Vault-relative file path to write |
| `directory` | optional | Vault directory (default: .) |

| Option | What it does |
|---|---|
| `--also` | Additional files to include atomically (repeatable) |
| `--file` | Read content from LOCAL_FILE instead of stdin |
| `--json` | Print result as JSON instead of plain text |
| `--message` | Commit message (auto-generated if omitted) |
| `--push` | Push immediately after writing; stdout contains only the blob ID |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/file.html)*
