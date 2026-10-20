---
title: Working with AI agents
summary: The agent-facing surface: sgit write, --json everywhere, the clone modes including scoped and shallow clones, the session pattern, and multi-agent collaboration.
section: guides
order: 3
moved_from: https://sgit.ai/docs/agents.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Working with AI agents

sgit is designed to be driven by AI agents as well as humans. A vault is just a folder. The agent reads and writes files normally; sgit handles versioning, encryption, and sync. This page covers the agent-facing surface.

## Network requirements

sgit needs HTTPS to your API server, by default `dev.send.sgraph.ai`, and agents reading these docs also need `sgit.ai`. Sandboxed agents, for example Claude on a Team or Enterprise plan, often sit behind an allowlisting proxy. If you see `CONNECT … 403`, the host is blocked, not down: ask the organisation's Owner to allow `sgit.ai`, `*.sgit.ai` and `*.sgraph.ai`, listing the apex domains explicitly. [The how-to](/docs/how-to/claude-team-egress.html) has the steps and a check to paste.

## The session pattern

```
# start of session: get the workspace
$ sgit clone <vault-key> workspace   # or: sgit pull, if already cloned
# … agent works on files normally …
# end of session: persist the state
$ sgit commit -m "session: findings and next steps"
$ sgit push
```

The next session (hours or weeks later, on any machine) runs `sgit pull` and continues. State survives the context window, encrypted end to end. On a vault that has grown large, an agent that works in one folder should clone only that folder: `sgit clone --path <folder> --depth 1`, seconds instead of minutes, with the same commit and push. [Partial clones](/docs/partial-clones.html) explains it; [Agents sharing one vault](/docs/agents-sharing-one-vault.html) is the loop for a team.

## `sgit write`, the surgical commit

When an agent needs to record one result, cloning a whole vault is waste. `write` commits a file directly to the vault HEAD in a single call: no working-directory scan, no full clone needed.

```
$ sgit write notes/finding.md --file result.md \
    --message "agent A: analysis" --push --json
{ "status": "pushed", "path": "notes/finding.md",
  "blob_id": "obj-cas-imm-9c2e41ab77d0" }
```

- `--also vault-path:local-file` (repeatable) makes a multi-file write **atomic**: one commit, all or nothing.
- Content-hash dedup: writing identical content returns `unchanged` and creates no commit.
- `--json` gives a machine-readable result for the calling pipeline.

## Machine-readable everything

| Need | Command |
|---|---|
| Read one file, structured | `sgit cat <path> --json` · `sgit cat --id <blob-id>` (zero network calls) |
| List files with fetch state | `sgit ls --json` / `--ids` |
| History for pipelines | `sgit history log --json` · `history diff --json` |
| Health checks | `sgit doctor --json` |

## Fast cold starts

Agents run on time budgets. Five clone modes keep startup cheap; the first two arrived in sgit-ai 0.18.0 and are the usual choice for an agent:

- `sgit clone --path <folder>`, a scoped clone: only the folders you work in, everything else carried by id. Writes outside the held folders are refused by name, and two scoped clones in different folders cannot conflict. Widen later with `sgit fetch <folder>`. On a 600-commit, 9,400-file vault: one folder in 14 s against 80 s for the whole vault.
- `sgit clone --depth 1`, a shallow clone: the whole tree at HEAD, no history. Combine with `--path`; deepen later with `sgit fetch --unshallow`.
- `sgit clone --sparse`, structure now, file content on demand via `sgit fetch <path>`. A scoped clone is usually the better fit, because it holds the files it will read without a round trip per file.
- `sgit clone-branch`, full history, but only HEAD's content.
- `sgit clone-headless`, credentials only: derive keys and write config, fetch nothing.

A full clone itself is about twice as fast since 0.18.0: the store is listed once and downloaded in one parallel sweep. Details, limits and measurements: [Partial clones](/docs/partial-clones.html).

## Multi-agent collaboration

For a team of agents on one vault, read [Agents sharing one vault](/docs/agents-sharing-one-vault.html) first: one folder per agent in a scoped clone, `sgit status` before committing, and what a pull does with work you have not committed, which since 0.18.0 is kept or refused by name rather than overwritten. Then the branch-level tools: give each agent a named branch; the [two-branch model](/docs/two-branch-model.html) guarantees isolation of work-in-progress. Two commands make peer review safe:

- `sgit history show <commit>` and `sgit history diff` are **read-only**: they fetch missing objects on demand without merging, so an agent can inspect a peer's commit without touching its own working copy.
- `sgit resolve --show` renders base/ours/theirs with a per-file verdict, so genuine conflicts are distinguishable from noise, by a human or by an agent.

```
# agent A  $ sgit branch new feature-analysis … commit … push
# agent B  $ sgit history show obj-cas-imm-c4e81a   # look, don't merge
# human    $ sgit pull → review in SG/Vault → merge
```

**For Claude users:** a packaged sgit Skill teaches a Claude session this entire workflow (install, clone, work, commit, push) so cross-session persistent state works out of the box.
