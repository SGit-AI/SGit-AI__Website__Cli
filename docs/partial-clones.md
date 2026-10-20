# Partial clones: a folder scope and a history depth, cli.sgit.ai

> sgit clone --path holds one folder and carries the rest by id; --depth holds the newest commits only. Measured on a 600-commit vault: one folder in 14 s against 80 s for the whole vault. The rules, widening with sgit fetch, the commands that need a full clone, and the two edges.

*Source: <https://cli.sgit.ai/docs/partial-clones.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/partial-clones.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Partial clones: a folder scope and a history depth

A full clone downloads every version of every file in the vault. For a small vault that is the right default. For a vault a team has worked in for months it is not: a few hundred commits and several thousand files mean minutes of download for an agent that will touch three files in one folder. Two options cut the clone down to what the work needs, and both keep `commit`, `push` and `pull` working normally.

For sgit-ai 0.18.0 or newer. Check with `sgit version`; upgrade with `sgit update` ([what changed](../docs/update-to-0-18-0.md); the current release is 0.21.0, [update notes](../docs/update-to-0-21-0.md)).

| Option | What the clone holds | Use it when |
|---|---|---|
| `--path <folder-name>` | The named folders, their files, and the folders on the way down to them. Everything else by id only. | You work inside one or a few folders. |
| `--depth N` | The whole tree at HEAD, but only the newest N commits of history. | You need the files, not the history. |
| both | The named folders, newest N commits. | An agent doing a bounded task in its own folder. The usual choice for agent teams. |

## Measured

On a shared CRM vault of about 600 commits and 9,400 files, from one client in a cloud sandbox whose network path adds latency to every request, so a plain connection does better. The numbers are the CLI team's, from the vault the release was built against.

| Clone | Time | Objects | Download |
|---|---|---|---|
| full | 80 s | 18,720 | 173 MB |
| `--path mail/crm.example` (one folder, 365 files) | 14 s | 429 | 3.2 MB |
| `--path runs --path docs` (two small folders) | 5 s |  |  |
| `--path mail/crm.example --depth 1` | 14 s |  |  |

Checked by this site on 7 October 2026 against a small published vault ([the Deck Vault](https://sgit.ai/demos/vaults/deck-vault/index.html), 55 files, 3 commits) from the same kind of sandbox: a full read-only clone took 9.7 s; `--path plan --depth 1` took 3.0 s and wrote the 11 files of that folder and nothing else. The ratio is what matters, and it grows with the vault.

## The example used on this page

A CRM vault maintained by a team of agents. Each agent has a mailbox-style folder it owns, plus shared folders. Most of an agent's session is reads and writes inside its own `mail/<my-account>/` folder.

```
mail/
  crm.example/        one agent's folder: contacts, threads, notes
  ops.example/        another agent's
runs/                 run logs, appended by everyone
docs/                 shared documents
README.md
```

## Scoped clone: `--path`

```
$ sgit clone --path mail/crm.example <vault-key> workspace

Cloned into workspace/
  Vault ID:  …
  Transport: api
  Branch:    branch-clone-…
  HEAD:      obj-cas-imm-…
  Scope:     mail/crm.example  (other folders carried by id; widen: sgit fetch <folder-name>)
$ cd workspace
$ find . -type f -not -path './.sg_vault/*'
./mail/crm.example/contacts.md
./mail/crm.example/threads/2026-10-06.md
...
```

Only the held folder is on disk. `sgit status`, `sgit ls` and `sgit cat` see the held folder. There is no `docs/` directory, and that is not an error: the clone knows `docs/` exists and what its id is, and carries that id untouched into every commit it makes.

Work normally inside the folder:

```
$ echo "called back" >> mail/crm.example/threads/2026-10-06.md
$ sgit status
On branch: branch-clone-… → branch-named-…
  Remote: in sync with remote

  ~ mail/crm.example/threads/2026-10-06.md
$ sgit commit -m "crm: call-back note"
$ sgit push
```

The pushed commit contains the whole vault, exactly as a full clone's commit would: your folder rebuilt, every other folder by the id the vault already had for it. A teammate on a full clone pulls it and sees only your change. The ids match byte for byte because tree encryption is deterministic; a test in the CLI suite asserts that a scoped commit's tree id equals the one a full clone would produce.

### Rules of a scoped clone

- **Writes outside the held folders are refused, by name.** `sgit commit` with a stray `docs/notes.md` in the working copy stops with the message `this clone holds only mail/crm.example; files outside it cannot be committed from here: docs/notes.md`. Widen the clone (below) or use a full clone for that change.
- **Two scoped clones in different folders never conflict.** Out-of-scope entries are always taken from the remote by id, so agent A in `mail/crm.example/` and agent B in `docs/` can commit and push in any order without a merge conflict. Two agents in the *same* folder merge like any two clones do.
- **Pull fetches only what is held.** A teammate's change to `docs/` costs a scoped clone one commit object and the folders on the spine, a few objects, not the changed files.
- **Uncommitted edits survive a pull**, exactly as on a full clone; see [Agents sharing one vault](../docs/agents-sharing-one-vault.md).
- **Several folders:** repeat the flag, `--path mail/crm.example --path docs`. A folder inside a held folder is already held; listing both collapses to the wider one.
- **Paths are vault-relative folders.** `..`, absolute paths and drive letters are refused.

### Widening later: `sgit fetch <folder-name>`

```
$ sgit fetch docs
  ✓  docs  (12 file(s), 15 object(s) fetched)
  Scope is now: mail/crm.example, docs
```

The folder is fetched from HEAD, written to disk and recorded in the clone's config, so it stays held across pulls and branch switches. Widening never overwrites your work: if a file is already on disk under that folder and its bytes differ from the vault's, the widen refuses and names it. Move the file aside and widen again. A folder already held returns at once.

### Commands that need the whole vault

`sgit check fsck`, `sgit dev dump`, `sgit publish` and `sgit vault move` stop on a scoped or shallow clone:

```
$ sgit check fsck
error: `sgit check fsck` needs the whole vault, and this clone holds only part of it
(folders: mail/crm.example). Run it from a full clone, or widen this one:
`sgit fetch <folder-name>` adds a folder, `sgit fetch --unshallow` fetches the history.
```

Any other command that happens to need an object the clone never fetched says the same thing in its own words, rather than suggesting the vault is corrupt.

## Shallow clone: `--depth N`

```
$ sgit clone --depth 1 <vault-key> workspace
…
  History:   shallow, 1 boundary commit(s)  (deepen: sgit fetch --unshallow)
```

The whole tree at HEAD and the newest commit only (N commits for `--depth N`). The commit where history stops is recorded as a boundary. `commit`, `push`, `pull` and `status` work normally; the named branch only ever moves forward, so every later commit descends from the boundary and the clone never needs what lies behind it. History commands stop there and say so:

```
$ sgit history log --oneline
a1b2c3d  crm: call-back note
  … history stops here: shallow clone (1 boundary commit); sgit fetch --unshallow fetches the rest
```

### Deepening later: `sgit fetch --unshallow`

On a whole-vault shallow clone this fetches everything behind the boundary in one parallel sweep, the same sweep a full clone uses. On a scoped shallow clone it fetches the commit objects only, which is what `history log` and `status` need; files and folders stay scoped. The command reports `History fetched: N object(s); this clone is no longer shallow.`, or `This clone already has the full history.` on a clone that is already full.

## Choosing

- **An agent that works in its own folder for a bounded task:** `--path <folder-name> --depth 1`. The clone is seconds, the push carries only the change, and nothing another agent does elsewhere in the vault can conflict with it.
- **An agent that reviews or rewrites across the vault:** a full clone. At 600 commits it is 80 s on the measured path, and the sweep keeps it close to linear in the vault's size.
- **A reader that wants one file:** no clone at all. `sgit cat` and `sgit write` work against the server directly; see [Working with AI agents](../docs/agents.md).
- **Sparse (`--sparse`) still exists:** structure now, file content on demand. A scoped clone is usually the better fit for an agent, because it holds the files it will read without a round trip per file.

## What a partial clone cannot do yet

- A folder renamed by someone else silently leaves your scope: the clone holds `mail/old/` by name, and after the rename the vault has `mail/new/` in its place. A pull will not warn. Re-clone or widen to the new name.
- Scoped clones cannot see objects missing elsewhere in the vault, so `sgit check fsck` needs a full clone.

Source: the CLI team's release brief for 0.18.0, 7 October 2026, with its measurements kept under the conditions it stated; the scope rules, the refusal messages, widening and the whole-vault refusal were re-run by this site against a published vault on the same day.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/partial-clones.html)*
