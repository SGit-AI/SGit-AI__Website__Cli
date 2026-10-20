---
title: Update sgit-ai to 0.21.0
summary: For an agent team: sgit update, what now refuses and what to do (symlinks, unreadable files, SGIT_DEFAULT_BASE_URL, key zips, branch names, rewinds, signatures), the new history commands (undo, reflog, amend, revert --as-commit, shorthand, log filters), signed tags, --force-with-lease, notes for vault owners and mixed 0.20/0.21 teams. Covers 0.19.0 and 0.20.0. Published 11 October 2026.
section: guides
order: 10
moved_from: https://sgit.ai/docs/update-to-0-21-0.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Update sgit-ai to 0.21.0

A page for an agent, or a person running agents, that has been told "read this and update". Ten minutes. sgit-ai 0.21.0 was published to PyPI on 10 October 2026. It includes everything in 0.19.0 and 0.20.0, so coming from 0.18.0 or older this is the only page you need. **Your daily loop does not change**: `pull`, work, `commit`, `push`. What changes is what sgit now refuses to do, and a set of history commands you have been missing.

## 1. Update and check

```
$ sgit update          # wraps: pip install --upgrade sgit-ai
$ sgit version
sgit-ai v0.21.0
```

If `sgit version` still shows an older number, you have more than one Python environment; run `python -m pip install --upgrade sgit-ai` in the one your harness uses, then check again. [Installation](/docs/installation.html) has the rest. Your existing clones need nothing: the first command in each one records the server it uses and moves its bookkeeping to the 0.21.0 layout.

## 2. What now refuses, and what to do

0.21.0 is a security release. Each of these used to work, or work silently and do damage. Each refusal names the file or branch and says what to do; none changes anything before it stops.

| You see | Why | What to do |
|---|---|---|
| `warning: skipped symlink <path>` on commit | sgit never stores, follows or writes through a link. A link to `.sg_vault/local/vault_key` used to commit the vault key itself | Nothing. Commit the real file if you meant to. A tracked file replaced by a link keeps its committed version; `status` and `pull` name it |
| `cannot read <file> (Permission denied); nothing was changed` | A file sgit cannot open used to read as deleted, and a commit removed it for everyone | Close the program holding it or fix its permissions, then run the command again |
| a refusal naming `SGIT_DEFAULT_BASE_URL` | The variable used to silently redirect a vault, with your token and write key, to whatever host it named | Name the server once: `sgit --base-url <url> <command>` (the flag goes before a group too), or `sgit remote add origin <url>`. Vaults made by 0.21.0 already record it |
| a commit refused over a zip that holds a key | A backup zip (or any zip) holding a vault key or a private signing key would hand it to every reader | Delete it, or move it out of the vault folder. `sgit commit --allow-secret-file <path>` commits one on purpose |
| `a branch named '<name>' already exists on the server` on push | A teammate pushed a branch with that name first; yours used to land where nobody could see it | `sgit branch rename <name> <new-name>`, then `sgit push` |
| `the named branch was REWOUND`; `push` exits 1 | Someone force-pushed, or the server served an old pointer | Do not accept it on your own; tell the vault owner. If it was deliberate: `sgit pull --accept-rewind`, which keeps your own unpushed commits and drops the removed ones |
| `this vault needs sgit-ai >= X.Y.Z` | The owner raised the vault's minimum client | `sgit update`, then retry |
| a pull, clone or push refused over an unsigned commit | The vault requires signed commits (`signatures-required`) | Tell the vault owner. If your clone has no signing key (it says `UNSIGNED` when you commit), clone the vault again |
| `'abcdef1' is not a valid tag name`, or a revision refused as ambiguous | A tag named like a commit id would shadow it | Pick another name. For an existing short-hex tag write `tag:<name>`, or the full commit id |
| `sgit: 'log' is now sgit history log` (exit 2) | Commands moved into groups in earlier releases | Use the name it prints |

## 3. New commands worth knowing

All local, all safe to try. Every example below is output from 0.21.0 on the live dev server, 11 October 2026.

### History, the way git users expect it

```
$ sgit history log --grep more --stat
  f7a8b9646ae9 (HEAD)  add more  ~1  [blobs:+1]
      M  notes.md

$ sgit history show HEAD~1
commit obj-cas-imm-bb27e943d81d
parent obj-cas-imm-326e87100964
    first notes
+ notes.md  (8 bytes)
```

- **Revisions everywhere a commit is named:** `HEAD`, `@`, `HEAD~2`, `HEAD^2`, `@{1}` (where this clone's head was), tag names, the 12-hex id `history log` prints, or any unique prefix of 4+ characters.
- **Log filters:** `--grep`, `--since` / `--until` (`2026-10-08`, `3d`, `"2 weeks ago"`, `yesterday`), `--author` (a signing key id or branch name), `--stat`. They follow merged-in commits too.

### Undo, amend, revert

```
$ sgit history undo
Undone: this clone's head is back at f7a8b9646ae9 (was d9c5d05ea052).
  1 file(s) restored, 0 removed. Run it again to redo; sgit history reflog shows every move.

$ sgit history reflog -n 3
  @{0}  f7a8b9646ae9  2026-10-11 15:54:26  add more  (was d9c5d05ea052)
  @{1}  d9c5d05ea052  2026-10-11 15:54:25  local mistake  (was f7a8b9646ae9)
  @{2}  f7a8b9646ae9  2026-10-11 15:54:09  add more  (was bb27e943d81d)
```

| Command | What it does | When |
|---|---|---|
| `sgit history undo` | moves this clone's head back to before its last move, restoring the files; run again to redo | a local commit you regret, before pushing |
| `sgit history reflog` | every move of this clone's head (local, last 1,000); `sgit history reset <id>` brings one back | after a reset, an accepted rewind or a bad merge |
| `sgit commit --amend [-m …]` | replaces the last commit; refused once it is on the server | a typo in the message, a forgotten file |
| `sgit history revert --as-commit --commit <rev>` | a new, signed commit that inverts an earlier one (git's `revert`) | undoing a **pushed** change for everyone |

Plain `sgit history revert` still restores files without committing, as before.

### Tags, branches, safer force

```
$ sgit vault tag create v1.0 -m "first release"
Tagged f7a8b9646ae9 as v1.0, signed by this clone.
$ sgit vault tag list
  ✓ v1.0  f7a8b9646ae9  2026-10-11 15:54 UTC  first release
```

- **Signed tags** (`sgit vault tag create | list | show | delete`): an encrypted, signed object; the name lives only in the encrypted branch index, so the server never sees it. Tags do not move without `--force`, and a pull reports a tag that moved. A tag name works wherever a commit does.
- **Branches work end to end:** `branch new`, `branch switch` (fetches first), `branch merge <name>`, and `branch rename` for a branch not yet pushed. Before 0.21.0, work on a branch was pushed to the main branch.
- **`sgit push --force-with-lease`**: forces only if the remote is still where this clone last accepted it, and writes with compare-and-swap, so a teammate's push is never clobbered. Running `status` in between does not satisfy the lease.
- **`sgit doctor`** names the server it checks and sends the same headers as push and pull; `sgit clone - <dir>` reads the vault key from stdin, so it never appears in your command line or shell history.

## 4. If you are the vault owner

Nothing changes for a vault until you raise it. 0.21.0 is the first release where the history-integrity features are safe for a team of writers.

```
$ sgit vault format --set 2 --min-client 0.21.0 --feature signatures-required
Vault format updated and written to the server.
  …
  Format:      2  (new objects get 32-hex ids)
  Min client:  0.21.0   (this client: v0.21.0)
  Features:    ids-128, signatures-required, signed-since-82bcf306a04a
```

- **`--min-client 0.21.0`** is the recommended floor: a 0.19.0 or 0.20.0 client is then refused by name (`this vault needs sgit-ai >= 0.21.0 and this is 0.20.0: run `sgit update``, checked on 11 October). It also keeps 0.20.0 clients from dropping the vault's tags, below.
- **`signatures-required`** now works with several writers. Clone, pull and push all check it. Only commits after the moment you switch it on (`signed-since-…`) must be signed, so older unsigned history is fine.
- **Clients older than 0.19.0 do not know the gate exists.** On a raised vault they fail and blame the data ("integrity check refused vault data", "missing file … sgit check fsck"). The fix for them is `sgit update`, never `vault move` or `fsck --repair`. Raise a vault only when every writer is on 0.21.0.

The whole model (the gate, 128-bit ids, rewinds, signatures) is in [History integrity](/docs/history-integrity.html).

## 5. Mixed teams: 0.20.0 and 0.21.0 on one vault

Clone, pull, commit and push work in both directions, and every commit verifies (checked live on 10 and 11 October). Two things to know:

- **Tags disappear while a 0.20.0 client is active.** The first push of a 0.20.0 clone leaves the server with no tags; a 0.21.0 clone that still holds them restores them on its next pull, but a fresh clone made in between sees none. For a vault that uses tags: `--min-client 0.21.0`.
- **A 0.20.0 backup has no signing key.** A clone restored from it makes unsigned commits (it warns `UNSIGNED`); under `signatures-required` it cannot push until it is cloned again. 0.21.0 backups carry the key.

**If anyone on your team is still on 0.20.0 or older:** after `sgit vault uninit`, delete the `*__uninit.zip` it leaves in the folder before the next `sgit commit`. On those versions the zip, which holds the vault key, is committed like any other file. 0.21.0 names it so it is never committed, and refuses any zip holding a key.

## 6. If you want the detail

- [sgit-ai 0.21.0, the release notes](https://sgit.ai/updates/index.html#sgit-ai-0-21-0): what changed since 0.18.0, and how it was checked.
- [History integrity](/docs/history-integrity.html): the format gate, signatures, rewinds and the checklist for raising a vault.
- [Agents sharing one vault](/docs/agents-sharing-one-vault.html): the recommended loop for a team.
- The CLI's full change log, with every fix: [CHANGELOG.md](https://github.com/SGit-AI/SGit-AI__CLI/blob/main/CHANGELOG.md).
