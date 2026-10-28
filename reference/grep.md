# sgit grep, cli.sgit.ai

> Search the files of the working copy or a revision, as git grep

*Source: <https://cli.sgit.ai/reference/grep.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit grep

Search the files of the working copy or a revision, as git grep.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. No subcommands. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit grep [options] [positionals]
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

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/grep.html)*
