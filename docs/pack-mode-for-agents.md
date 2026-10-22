# Pack mode: a playbook for agents, cli.sgit.ai

> Everything an agent needs to use sgit pack vaults (sgit-ai 0.24.0 and later) in a project, as recipes to follow in order. Decide whether a vault should be a pack vault; create one, or convert a copy of an existing vault and cut a team over to it; the daily loop and what its output should look like; who compacts, when, and how; the patterns for CI jobs, many agents, read-only readers and throwaway vaults; the health checks; every error message an agent will meet, with what to do; what never to do; and a block to paste into an agent's own instructions.

*Source: <https://cli.sgit.ai/docs/pack-mode-for-agents.html> · generated from the same content as the page, so the two cannot drift.*

---
# Pack mode: a playbook for agents

This page is written for an agent that has been told to use sgit pack vaults in a project. It is also for the person setting that agent up. Follow the recipes in order. Every command and every message quoted here was run against sgit-ai 0.24.0 on `dev.send.sgraph.ai`. What a pack vault is, and the numbers, are in [the 0.24.0 release notes](../docs/update-to-0-24-0.md).

## 0. Three rules before anything else

1. **Experiment on a vault you created for the experiment.** Never on a vault other people or agents are using. Delete it when you are done: `sgit vault delete-on-remote --yes` inside its folder.
2. **A vault key is the whole credential.** Print it once, save it where your project keeps secrets, and never write it into a file inside a vault, a log, a commit message or a chat.
3. **Never copy, zip or commit `.sg_vault/local/`.** It holds this clone's key and token. The shareable part of a vault is `.sg_vault/bare/`.

## 1. Install and check

```text
$ python -m pip install --upgrade sgit-ai
$ sgit version
sgit-ai v0.24.0                      # 0.24.0 or later; an older client is refused by every pack vault
$ sgit pack --help                   # lists import, export, compact, ls, verify, stats
```

**Credentials.** Network commands need the server and an access token:
- Pass `--base-url <server>` and `--token <token>` on the first network command in a folder.
- sgit records both in that clone's `.sg_vault/local/`, so later commands in the same folder need neither.
- **No environment variable is read for the token.** Exporting one does nothing.
- To change the server for a clone, run `sgit remote add origin <url>` inside it.

## 2. Decide: pack vault or normal vault

| The vault will be … | Choose | Why |
|---|---|---|
| Cloned whole, by CI jobs or by agents starting fresh | **pack** | A clone is 3 or 4 requests whatever the history: 8.1 s against 28.6 s on a 2,087-object vault, 25 s against 3½ minutes on a 33,000-object history |
| Mostly text: Markdown, JSON, logs, email | **pack** | Files are compressed before encryption: 1.66× on a mixed vault, 3.7× on prose and JSON, 8.8× on JSONL logs |
| Pushed to often, by several writers | **pack** | A push is one zip whatever its size, and the ref moves exactly as before |
| Browsed in the web view (vault.sgraph.ai, a vault app, a published vault page) | **normal** | The browser does not read packs |
| Large, with agents that each take **one folder** (`--path <folder> --depth 1`) | **normal**, for now | On a pack vault `--path` and `--depth` download the packs whole; on a normal vault one folder of a 527 MB vault is 3 MB |
| Read with `clone-branch` or `clone-range` | **normal** | Those two refuse a pack vault |

When in doubt, use a pack vault for anything an agent clones whole and a normal vault for anything a person browses. You can move between the two later (section 4).

## 3. Recipe: a new pack vault

```text
$ mkdir my-vault && cd my-vault
$ sgit init --packs --base-url https://dev.send.sgraph.ai
Vault created!  Vault ID: <id>  (pack vault)
  Vault key: <the key: save it now>
$ # … add files …
$ sgit commit -m "first"
$ sgit push --token <token>          # the first push uploads one snapshot
```

`sgit create --packs <name>` does the same in one step: it makes the folder, the vault and the first push.

To join a pack vault that already exists, `sgit clone <vault key> <dir> --base-url <server> --token <token>`. The clone prints what it fetched:

```text
  ▸ Packs fetched (1 pack(s), 2087 objects, 4 request(s) in 6.2s)
```

The request count stays at 3 or 4 whatever the size of the history. **If a clone of a pack vault ever reports fetching objects one by one, stop and report it** (section 9).

## 4. Recipe: convert an existing vault, and cut a team over to it

A vault is never converted in place. You make a **new** pack vault from a **full** clone of the old one, check it, hand out the new key, and keep the old vault until nobody needs it.

```text
# 1. Stop writes to the old vault (tell the other agents), then take a FULL clone
$ sgit clone <old vault key> old-full --base-url <server> --token <token>
#    (no --path, no --depth: see the note below)

# 2. Make the pack vault (local only, nothing is uploaded yet)
$ sgit pack import old-full new-packs
  Imported into a new pack vault: new-packs/
  Vault key: <the NEW key: save it now>
  History:   17 commits, 244 trees, 1826 blobs
  Blobs:     213.0 MB -> 128.6 MB (x1.66, 1811 deflated)

# 3. Check, then push
$ cd new-packs && sgit status       # "This vault has never been pushed … 17 commits waiting"
$ sgit push                         # "Pushed 17 commit(s), 2087 object(s) uploaded."

# 4. Prove it: a fresh clone must match the old one file for file
$ cd .. && sgit clone <NEW key> check --base-url <server> --token <token>
$ diff -rq old-full check -x .sg_vault && echo IDENTICAL
```

Things to know:
- **The source must be a full clone.** On a `--path` or `--depth` clone the import stops with `missing file — object … is not in the local store` and a hint about corruption. The vault is not corrupt: the clone simply does not hold the whole history. The import also leaves a half-made vault in the target folder. Delete that folder (never push it), take a full clone, and run the import again.
- **The new vault is created on the source's server.** For a different server, pass `--base-url` to `pack import`, or run `sgit remote add origin <url>` in `new-packs/` before step 3.
- **The history is rewritten under the new key:** same files, same messages and timestamps, new commit ids, every commit re-signed by the importing clone.
- **Cut-over.** Replace the old key with the new one wherever agents read it, have every agent clone the new vault fresh, and only then retire the old vault. Agents' old clones cannot pull from the new vault: it is a different vault.
- **To go back,** `sgit pack export <pack clone> <new dir>` makes a normal vault with its own key, the same way. Push it, check it the same way.
- **Uncompressed packs:** `sgit pack import --no-deflate` keeps file contents uncompressed. Use it if the server must not learn how compressible each file is (section 10).

## 5. The daily loop

Nothing changes:

```text
$ sgit pull
$ # … work …
$ sgit commit -m "what changed"
$ sgit push
```

What the output should look like:
- **A push** uploads one commit pack: `Pushed 1 commit(s), 4 object(s) uploaded.` If another agent pushed first, push pulls and merges before it uploads, as on any vault.
- **A pull** fetches the commit packs this clone has not seen, in one batch.
- **`sgit status`** works as on a normal vault.
- **Every local command** (`history log`, `cat`, `diff`, `branch`, `stash`, `vault tag create`) works as on a normal vault, because the local store is unchanged.

Expect a few seconds per network command: about 5 to 6 s for a push and 3 to 4 s for a pull on a 2,000-object vault from a cloud sandbox. On a long history, push and pull also spend time in local merge and status walks. That is the same on a normal vault.

## 6. Compaction: who, when, how

Every push adds one small zip to `bare/packs/commits/`. Compaction folds them into one new snapshot of the head and moves the old zips to `bare/packs/archive/`. Nothing is ever deleted without its copy being listed in `archive/` first, and `archive/` itself is never deleted.

**Who.** Give the job to one agent, or to the vault's owner. Two compactions at the same moment are safe (tested live: both finish, the vault is intact), but they do the same work twice.

**When.** When `commits/` holds more than 50 packs, or more bytes than a tenth of the newest snapshot (sgit's own thresholds). Nothing triggers it automatically. Check with `pack ls --json`, which only lists the host:

```text
$ sgit pack ls --json > packs.json
$ python3 -c "import json; d=json.load(open('packs.json')); c, s = d['commits'], d['snapshots']; \
  print('compact' if len(c) > 50 or sum(e['size'] for e in c) > 0.10 * (s[-1]['size'] if s else 0) else 'not yet')"
```

Avoid `pack stats` for this check on a big vault. It decrypts every file to compute the compression ratio, which took 52 s on a 33,000-object history.

**Run it when the team is quiet.** After a compaction, every clone that was behind downloads the whole new snapshot on its next pull (130 MB and 9.5 s on a 2,087-object vault), instead of the few packs it lacked.

**How:**

```text
$ sgit pull                                    # compaction refuses a clone that is behind
$ sgit status                                  # and a dirty working tree
$ sgit pack compact --dry-run                  # the plan: what goes to archive/
$ sgit pack compact
  Did snapshot head obj-cas-imm-…: <epoch>__obj-cas-imm-…__<bytes>.zip
  3 pack(s) absorbed by the snapshot -> archive/
  1 pack(s) superseded snapshots -> archive/
  4 pack(s) archived. Nothing was deleted without its copy in archive/.
$ sgit pack verify                             # every member of every pack checked: "ok"
```

What gets archived and what stays:
- **Packs of other branches stay.** Compaction judges what is reachable from every ref on the host, not only this clone's branch, so a `push --branch-only` or another named branch keeps its packs.
- **Orphan commit packs are archived** once they are more than a day old.
- **If the branch moves while compaction runs,** it stops before archiving anything and says so. Pull and run it again.

## 7. Patterns

**A CI job.**
- Clone, work, commit, push.
- Pass the key and token from the CI system's secrets, never from the repository.
- A pack vault suits a job that needs the whole vault. A job that needs one folder of a big vault is better served by a normal vault and `--path` (section 2).
- The job's clone is thrown away with the runner, and nothing in `bare/` needs caching: the snapshot is one download.

```text
sgit clone "$VAULT_KEY" work --base-url "$SGIT_SERVER" --token "$SGIT_TOKEN"
cd work && ./run-the-job.sh && sgit commit -m "run $RUN_ID" && sgit push
```

**Many agents on one vault.**
- Each agent has its own clone in its own folder. Never share a working folder between agents.
- A push that finds another agent's commit first pulls, merges and pushes, as on any vault.
- Agents that should not touch the named branch can push their clone branch only (`push --branch-only`). Compaction keeps those packs.

**Read-only readers.** A clone made with a read key takes and pulls packs. It cannot push or compact, and it says so.

**A throwaway vault per task.** `sgit create --packs <name>`, work, then `sgit vault delete-on-remote --yes` when the task is done. Check the deletion: a clone with the old key must now fail.

## 8. Health checks

| Check | Good | Not good |
|---|---|---|
| `sgit pack ls` | `snapshots/` 1 or more, `commits/` some, `archive/` growing over time; `*` marks what this clone absorbed | `snapshots/` empty on a vault that has been pushed |
| `sgit pack stats` | `loose objects under bare/data/: 0` (tag objects are counted apart) | any loose objects: something wrote a normal object into a pack vault |
| `sgit pack verify` | `N pack(s), M member(s) checked against their ids` then `ok` | anything else |
| A fresh clone | `Packs fetched (…, 3 or 4 request(s) …)` and `diff -rq` against a working clone is empty | objects fetched one by one, or a difference |

## 9. Messages you will meet, and what to do

| Message | Meaning | What to do |
|---|---|---|
| `this vault needs sgit-ai >= 0.24.0 and this is 0.23.0: run sgit update, then try again` | The client is older than pack mode | `python -m pip install --upgrade sgit-ai`, check `sgit version`, retry |
| `this is a pack vault (objects travel as packs): sgit clone-branch and clone-range do not read packs yet. Use sgit clone (or clone-headless, whose fetch does).` | Those two clone modes do not read packs | Use `sgit clone`, or `sgit clone-headless` then `sgit fetch <path>` |
| `no access token configured. Pass --token …` | This folder has no saved token | Pass `--token <token>` once; it is saved for the folder |
| `working directory has uncommitted changes; commit or stash them, then compact` | Compaction needs a clean tree | Commit or stash, then compact |
| `this clone's named head (…) is not the server's (…): run sgit pull first, then compact` | Someone pushed since your last pull | `sgit pull`, then compact |
| `the named branch moved while compacting: nothing was archived (the snapshot … stays on the host). Pull and run sgit pack compact again.` | A push landed during compaction | `sgit pull`, then compact again. The extra snapshot is harmless and the next compaction archives it |
| `… pack(s) archived (n already in archive)` | Another compaction of the same head did part of the work | Nothing |
| `This vault has never been pushed. It only exists on this machine.` | A new or freshly imported vault | `sgit push` |
| A pull or clone that names a pack and refuses its members | A pack failed its checks; nothing from it was written | Stop, do not retry in a loop, and report it (below) |

**Reporting a problem.** Send the output of `sgit version`, the exact command, the command again with `--debug`, and the output of `sgit pack ls` and `sgit pack verify`. Never send the vault key, the token or anything from `.sg_vault/local/`.

## 10. Never

- Never copy, zip or commit `.sg_vault/local/`.
- Never delete anything under `bare/packs/` by hand. Above all never `archive/`: it is where compaction keeps the only copy of history it has folded.
- Never compact with a dirty tree or a stale clone. sgit refuses both; do not work around the refusal.
- Never run `pack import` on a partial clone, and never push what such an import leaves behind (section 4).
- Never point the web view at a pack vault and conclude it is empty. The browser cannot read packs.
- Never assume compression is free of leaks. The server learns how compressible each file is. If that matters, import with `--no-deflate`.

## 11. A block for an agent's own instructions

Paste this into the instructions of an agent that will use a pack vault, with your own values in the first three lines:

```text
## Vault (sgit pack vault)
- Server: https://dev.send.sgraph.ai
- Vault key: in <where your project keeps secrets>; never print it, never write it into a file in the vault.
- Token: passed once with --token on the first network command in a folder; sgit saves it in .sg_vault/local/.
- Requires sgit-ai >= 0.24.0 (`sgit version`). Playbook: https://cli.sgit.ai/docs/pack-mode-for-agents.md
- Start of a session: `sgit pull`. End: `sgit commit -m "<what changed>"` then `sgit push`.
- Use `sgit clone`, never clone-branch or clone-range. --path/--depth download the whole vault on a pack vault.
- Do not run `sgit pack compact` unless you are the designated compactor.
- Never copy, zip or commit .sg_vault/local/; never delete anything under bare/packs/.
- If a pack fails its checks, or a clone fetches objects one by one: stop and report
  (sgit version, the command, --debug output, `sgit pack ls`, `sgit pack verify`), with no keys.
```

*Written by cli.sgit.ai's build agent on 22 October 2026, from the CLI's code at the 0.24.0 merge and from live trials on dev.send.sgraph.ai. The CLI team's own pages are the [feature reference and the tester's how-to](https://github.com/SGit-AI/SGit-AI__CLI/tree/dev/team/humans/dinis_cruz/claude-code-web).*

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/pack-mode-for-agents.html)*
