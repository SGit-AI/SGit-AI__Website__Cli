---
title: Agents sharing one vault
summary: The loop for a team of agents on one vault with sgit-ai 0.18.0: a scoped shallow clone per session, status before commit, push that pulls first, and the full table of what a pull does with uncommitted work: kept when untouched, refused by name when it would be overwritten.
section: guides
order: 4
moved_from: https://sgit.ai/docs/agents-sharing-one-vault.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Agents sharing one vault

For a team of agents that keep one vault between them: several of them cloning, committing and pushing at the same time, each many times a day, with a vault that has grown to hundreds of commits. Everything on this page was worked out on exactly that setup, a shared CRM vault maintained by around ten agents, and the numbers are from it.

For sgit-ai 0.18.0 or newer. The practices here depend on behaviour that older versions do not have; check with `sgit version`, upgrade with `sgit update` ([what changed](/docs/update-to-0-18-0.html); the current release is 0.21.0, [update notes](/docs/update-to-0-21-0.html)).

## The loop

Each agent, each session:

```
$ sgit clone --path mail/<my-account> --depth 1 <vault-key> workspace   # once per session, 5 to 15 s
$ cd workspace
# … read and write files inside mail/<my-account>/ …
$ sgit status                       # what changed, and whether the remote moved
$ sgit commit -m "what I did"
$ sgit push                         # pulls first, merges, uploads only what is new
```

Why each line is the way it is:

**Clone scoped and shallow.** An agent that works in one folder has no use for the other agents' folders or for months of history. On the example vault the full clone is 80 s and 173 MB; one folder with one commit of history is 14 s and 3 MB, two small folders are 5 s. Agent harnesses often give a command two or three minutes; a full clone of a growing vault crosses that eventually, a scoped clone does not. Details and limits: [Partial clones](/docs/partial-clones.html).

**Keep the clone for the session, not forever.** A clone directory is cheap to make. An agent that resumes an old clone starts with a stale working copy and an old `sgit`; a fresh clone starts current.

**`sgit status` before you commit.** It says what the remote has done since you cloned, with real numbers:

```
On branch: branch-clone-… → branch-named-…
  Remote: remote has 3 new commits — run: sgit pull
```

`50+` means more than status fetched to count; it is a lower bound, not a guess. Before 0.18.0 this line could say your fresh clone was hundreds of commits *ahead* when it was one commit behind. That is fixed.

**`sgit push` pulls first.** It merges what others pushed, then uploads. Only new objects go up: your commit, the folders on the way down to your change, and the changed files.

## What happens to work you have not committed

This is the behaviour the team most needed and the one that changed in 0.18.0. A pull used to write the whole incoming tree over the working copy, so an edit you had not committed yet was replaced by the committed version, even when the incoming commits never touched that file, and `sgit status` then reported the vault in sync. Three agents reported losing work that way in one week.

A pull now follows git's rules, and decides before it writes anything:

| Your working copy | The incoming commits | Result |
|---|---|---|
| changed `threads/today.md`, not committed | did not touch it | kept; pull reports `Kept 1 uncommitted change(s) the incoming commits did not touch` |
| changed `threads/today.md`, not committed | changed it too | pull refused, nothing written |
| deleted `old.md`, not committed | did not touch it | stays deleted |
| deleted `old.md`, not committed | changed it | pull refused |
| created `new.md`, not tracked | created `new.md` with the same bytes | fine |
| created `new.md`, not tracked | created `new.md` with different bytes | pull refused |
| created `scratch.md`, not tracked | nothing | left alone |

A refused pull looks like this and has changed nothing, on disk or in the store:

```
$ sgit push
error: your local changes would be overwritten by pull:
  mail/crm.example/threads/today.md  (your uncommitted edit would be overwritten)
commit them (sgit commit) or stash them (sgit vault stash) and pull again; nothing was changed
```

Do what it says: `sgit commit`, then push again; the merge happens on committed work, where a conflict is visible and resolvable (`sgit resolve`). An agent should treat this message as a normal outcome, not an error to retry.

"Changed" is measured the way `sgit status` measures it, by content rather than timestamps, so the two never disagree.

Re-run by this site on 7 October 2026 on a throwaway vault with sgit-ai 0.18.0: a scoped clone with an uncommitted edit pulled a teammate's commit to another folder and kept the edit; a full clone with an uncommitted edit to a file the incoming commit changed was refused by name, and the file was untouched afterwards. `sgit status` on both read `remote has 1 new commit`.

## Staying out of each other's way

- **One folder per agent, scoped clones.** Two scoped clones in different folders cannot produce a merge conflict: each carries the other's folder by id and only its own folder rebuilt. Shared folders (`runs/`, `docs/`) are where conflicts can happen; keep writes there append-only or one-owner where you can.
- **Many agents cloning at once is fine.** Reads go through 16 parallel connections per client, reuse one TLS connection per host, and a throttled request (HTTP 429) is retried with back-off. Ten agents cloning in the same minute will not fail each other.
- **Commit often, push when a unit of work is done.** Every pushed commit's files are uploaded, a 0.18.0 fix: a file created and changed again before one push used to leave its first version missing on the server. If a clone made before 0.18.0 pushed such a commit, `sgit check upload-objects` from that clone sends the missing objects.
- **`sgit push --branch-only`** shares work in progress without touching the named branch. It sends only what the server does not already have.

## When something is slow or fails

- **Clone slower than expected?** Check it is scoped: a clone that only holds `mail/…` has no `docs/` on disk. A full clone of a 600-commit vault is 80 s on a laggy path; if yours takes minutes, run `sgit version`: the sweep that makes it 80 s arrived in 0.18.0.
- **`error: … needs the whole vault`:** you are on a partial clone and ran `fsck`, `dump`, `publish` or `vault move`. Use a full clone for those.
- **`error: this clone holds only part of the vault … needs more of it`:** a command met an object the scope never fetched. Widen with `sgit fetch <folder-name>` or `sgit fetch --unshallow`, or use a full clone.
- **`sgit doctor`** checks the remote, the token and the version.

## A session, end to end

```
$ sgit update && sgit version
sgit-ai v0.18.0
$ sgit clone --path mail/crm.example --depth 1 <vault-key> work && cd work      # 14 s
$ sgit cat mail/crm.example/contacts.md
…
$ printf '\n- 2026-10-07: called, left message\n' >> mail/crm.example/threads/acme.md
$ sgit status
  ~ mail/crm.example/threads/acme.md
$ sgit commit -m "crm: acme call"
$ sgit push
Merged (no file changes).

Push complete. Named branch updated.
  Pushed 1 commit(s), 6 object(s) uploaded.
  commit obj-cas-imm-…
```

Six objects: the commit, the new root tree, the new `mail/` tree, the new `mail/crm.example/` tree, its new `threads/` tree, and the one changed file. Everything else in the vault was carried by id.

The team this was worked out on is described in [The agent team as it runs](https://sgit.ai/articles/the-agent-team-as-it-runs.html) and [The Mandate Stack](https://sgit.ai/articles/the-mandate-stack.html); the vault is their shared memory layer.
