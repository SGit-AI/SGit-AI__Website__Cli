---
title: sgit for git users
summary: The Rosetta stone: every git command mapped to its sgit equivalent, plus the three deliberate differences.
section: start
order: 4
moved_from: https://sgit.ai/docs/sgit-for-git-users.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# sgit for git users

If you know git, you know most of sgit. Same verbs, same mental model, with three deliberate differences that exist because the payload is encrypted.

> **Updated, 28 October 2026, against sgit-ai 0.26.0.** sgit is not only Git with encryption: it does twelve things Git has no equivalent for, and Git is still ahead on sixteen. The map is [sgit and Git](/docs/sgit-and-git.html). Rows below gained `write`, the clone options and `checkout`.

## The Rosetta stone

| git | sgit | Notes |
|---|---|---|
| `git init` | `sgit init` | `--existing` vault-ifies a non-empty folder |
| `git clone <url>` | `sgit clone <vault-key>` | the key is URL + auth + decryption in one |
| `git status` | `sgit status` | `--explain` teaches the branch model |
| `git commit -am` | `sgit commit -m` | the whole folder. There is no staging area |
| `git commit <paths>` | `sgit write <path> --file F --also P:F` | whole files, committed atomically to HEAD; other edits stay uncommitted; `--push --json` for agents |
| `git clone --filter` + sparse-checkout | `sgit clone --path FOLDER`, `sgit fetch FOLDER` | a commit outside the scope is refused by name |
| `git clone --depth` / `fetch --unshallow` | `sgit clone --depth N` / `sgit fetch --unshallow` | |
| `git clone --no-checkout` + `git checkout -- <paths>` | `sgit clone --no-checkout` + `sgit checkout <paths>` | `pull --no-checkout`, then `checkout --since-pull` writes only what changed |
| `git tag -s` | `sgit vault tag` | signed |
| `git push / pull / fetch` | `sgit push / pull / fetch` | push is delta + ciphertext only |
| `git log` | `sgit history log` | `--oneline`, `--patch`, `--json`, ranges |
| `git diff` | `sgit history diff` | `--remote`, `--commit`, `--files-only` |
| `git show` | `sgit history show` | read-only, fetches missing objects without merging |
| `git revert / reset` | `sgit history revert / reset` |  |
| `git stash` | `sgit vault stash` | `pop`, `list`, `drop` |
| `git branch / checkout` | `sgit branch new / switch / checkout` |  |
| `git merge` conflicts | `sgit resolve --show` | three-way base/ours/theirs view with a verdict per file |
| `git remote` | `sgit remote add / list / set-url` |  |
| `git fsck` | `sgit check fsck` | verifies encrypted object integrity, can repair |

## The three differences that matter

### 1. No staging area

`sgit commit` snapshots the whole folder. This removes git's most confusing concept. To commit some files and not others, `sgit write` commits the named files whole and leaves the rest uncommitted. What does not exist is choosing hunks within a file.

### 2. The vault key is URL, auth, and encryption key in one

`passphrase:vault-id`. There is no separate remote URL to configure, no separate credential to manage, and no password reset. Whoever holds the key holds the vault, treat it like the private key it is.

### 3. Two layers of branches

You never work directly on a shared branch. Every clone works on a private **clone branch** (its key never leaves your machine) and `push` forwards commits to the shared **named branch**. That's why two agents on the same vault can't corrupt each other's work-in-progress. [The full story →](/docs/two-branch-model.html)
