# sgit for git users, cli.sgit.ai

> The Rosetta stone: every git command mapped to its sgit equivalent, plus the three deliberate differences.

*Source: <https://cli.sgit.ai/docs/sgit-for-git-users.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/sgit-for-git-users.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# sgit for git users

If you know git, you know most of sgit. Same verbs, same mental model, with three deliberate differences that exist because the payload is encrypted.

## The Rosetta stone

| git | sgit | Notes |
|---|---|---|
| `git init` | `sgit init` | `--existing` vault-ifies a non-empty folder |
| `git clone <url>` | `sgit clone <vault-key>` | the key is URL + auth + decryption in one |
| `git status` | `sgit status` | `--explain` teaches the branch model |
| `git commit -am` | `sgit commit -m` | always whole-folder. There is no staging area |
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

Every commit snapshots the whole folder. This removes git's most confusing concept, and it fits the security model: partial staging would leak "which parts changed" into workflows that are supposed to be opaque. Use branches where you would have used the index.

### 2. The vault key is URL, auth, and encryption key in one

`passphrase:vault-id`. There is no separate remote URL to configure, no separate credential to manage, and no password reset. Whoever holds the key holds the vault, treat it like the private key it is.

### 3. Two layers of branches

You never work directly on a shared branch. Every clone works on a private **clone branch** (its key never leaves your machine) and `push` forwards commits to the shared **named branch**. That's why two agents on the same vault can't corrupt each other's work-in-progress. [The full story →](../docs/two-branch-model.md)

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/sgit-for-git-users.html)*
