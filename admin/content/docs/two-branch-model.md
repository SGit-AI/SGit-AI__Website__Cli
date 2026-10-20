---
title: The two-branch model
summary: sgit's central idea: private clone branches per machine or agent, shared named branches, and explicit publishing.
section: start
order: 5
moved_from: https://sgit.ai/docs/two-branch-model.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# The two-branch model

sgit's central architectural idea: every clone works on a private branch, and sharing is an explicit act.

## Clone branches and named branches

```
        agent A's machine                    the server                    agent B's machine
  ┌───────────────────────┐        ┌───────────────────────────┐        ┌───────────────────────┐
  │  clone branch (A)     │  push  │   named branch "main"     │  pull  │  clone branch (B)     │
  │  key: local only ─────┼───────▶│   key: shared via vault   │◀───────┼─ key: local only      │
  └───────────────────────┘        └───────────────────────────┘        └───────────────────────┘
```

- **Named branches** (`main`, `feature-x`, …) are shared and live on the server, encrypted, like everything else.
- **Clone branches** are created per clone. Their key is stored only in `.sg_vault/local/` and is never pushed. All your commits land here first.
- `sgit push` re-encrypts your clone-branch commits with the named branch's key and forwards them. `sgit pull` brings named-branch commits down and merges them into your clone branch.

Run `sgit status --explain` any time, it prints this model with your vault's actual branch names filled in.

## Why it works this way

- **Isolation by construction.** Two machines, or two agents, on the same vault physically cannot overwrite each other's uncommitted or unpushed work: they're on different branches with different keys.
- **Sharing is explicit.** Nothing you commit is visible to anyone until you `push`. An agent can iterate messily in private and publish only the result.
- **Safe concurrent pushes.** Pushes use compare-and-swap on the server (atomic batch writes): if someone pushed before you, your push is rejected cleanly instead of silently clobbering, pull, merge, push again.

## Merging and conflicts

When histories diverge, sgit runs a genuine three-way merge (common ancestor + ours + theirs) per file. Non-conflicting changes merge automatically; conflicting paths get `.conflict` files, and:

```
$ sgit resolve --show
  notes/plan.md   CONFLICT (both changed)
    base   │ ship in Q3
    ours   │ ship in Q4          ← your clone branch
    theirs │ ship in Q3, beta Q2 ← the named branch
    verdict: genuine conflict  (not one-sided, not identical)
```

The verdict line matters in multi-writer vaults: it distinguishes genuine conflicts from one-sided or identical changes, so you (or an agent) only spend attention where a human decision is actually required. `sgit merge-abort` backs out of a merge cleanly.
