---
title: Command reference
summary: Every sgit command, subcommand, argument and option, generated from the CLI's own parser (sgit help all --format json), grouped by what it is for.
section: reference
order: 0
hub: true
---

# Command reference

All **{{command_count}} commands** of **sgit-ai {{cli_version}}**, generated from the parser the CLI actually builds. The CLI walks its own argparse tree (`CLI__Reference`, behind `sgit help all --format json`, schema `sgit-cli-reference-v1`); this site renders that JSON and nothing else. A flag cannot appear here unless the code registers it, and none the code registers can be missing.

- The same data, as published: [sgit-cli-reference.json](/reference/sgit-cli-reference.json). Diff two releases' files to see exactly what changed.
- Your installed version, offline: `sgit help all`, or `sgit help <command>`.
- Global options go before the command: `sgit [--base-url URL] [--token TOKEN] [--vault PATH] [--debug] <command> ...`.

Where to put a new command is a rule of the CLI (its `CLAUDE.md`): a daily-use verb at the top level, anything about the vault as a whole under `vault`, anything about commits under `history`, checks under `check`.

!commands

## How this page is made

`admin/content/reference/sgit-cli-reference.json` is the output of `sgit help all --format json` from the release named above, installed from PyPI. The build turns it into one page per top-level command. To update: install the new release, run the command into that file, rebuild, and say in the release history which version the reference moved to.
