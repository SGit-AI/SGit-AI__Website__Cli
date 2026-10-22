---
title: sgit-ai 0.24.0 release notes: pack mode
summary: Release notes for sgit-ai 0.24.0, for people and agents. Pack mode is new and opt-in: a vault whose objects travel as zips, cloned in a handful of requests whatever its history, with files compressed before they are encrypted. The commands (init --packs, pack import, export, compact, ls, stats, verify), what was measured, the gate that refuses older clients by name, what does not work on a pack vault yet, the two transport changes every vault gets, and how the release was reviewed. Normal vaults behave as before.
section: guides
order: 9
---

# sgit-ai 0.24.0: pack mode

The release notes for 0.24.0, written to be read by a person or handed to an agent. **If you do nothing, nothing changes**: existing vaults stay normal vaults, and your daily loop (`pull`, work, `commit`, `push`) is the same. What is new is a second kind of vault, a **pack vault**, which you opt into for a new vault or by converting a copy of an existing one. To start using it, see [Pack mode: a playbook for agents](/docs/pack-mode-for-agents.html).

## 1. Update and check

```text
$ sgit update          # wraps: pip install --upgrade sgit-ai
$ sgit version
sgit-ai v0.24.0
$ sgit pack --help     # lists import, export, compact, ls, verify, stats
```

If `sgit version` shows an older number, you have more than one Python environment. Run `python -m pip install --upgrade sgit-ai` in the one your harness uses. Existing clones need nothing.

## 2. What is new: pack vaults

A normal vault stores every object as its own file on the host, so a clone of a long history is thousands of requests. A pack vault stores them as zips:

- **Every push uploads one zip** holding the commit's new objects. The ref then moves under compare-and-swap, exactly as before.
- **The first push, and each compaction, uploads one snapshot zip** holding the whole history.
- **A clone takes the snapshot for the branch head plus the commit zips since it.** That is three or four requests, whatever the size of the history.
- **A pull that is N pushes behind** is two listings and one batch of N zips.

**Files are compressed before they are encrypted**, so a text-heavy vault holds about half the bytes on the host. The server is unchanged: pack mode uses the batch, presigned, list and delete routes it already had.

The local store stays one file per object. Packs are unpacked on arrival, each object checked against its content address before it is written. So every local command (`history log`, `cat`, `diff`, `branch`, `stash`, `vault tag`) works exactly as on a normal vault.

| Command | What it does |
|---|---|
| `sgit init --packs [dir]`, `sgit create --packs <name>` | A new pack vault. |
| `sgit pack import <normal clone> <new dir>` | Rewrites a **full** clone of a normal vault into a **new** pack vault with its own key. The commits keep their messages and timestamps and are re-signed by the new clone. The source is untouched. The new vault's first `sgit push` uploads one snapshot. `--no-deflate` keeps file contents uncompressed; `--json` prints the stats. |
| `sgit pack export <pack clone> <new dir>` | The reverse: a **new** normal vault, nothing packed, nothing compressed. |
| `sgit pack compact [dir] [--dry-run]` | One snapshot of the current head. The packs it absorbs, the snapshots it supersedes and orphan packs older than a day move to `bare/packs/archive/`. Each is copied, the copy confirmed by listing, and only then the original deleted; `archive/` is never deleted. |
| `sgit pack ls`, `sgit pack stats`, `sgit pack verify` | What the host holds, folder by folder; packs and bytes plus the local compression ratio; every member of every pack checked against its content address. All three take `--json`. |
| `push`, `pull`, `clone`, `status` | Unchanged to use. On a pack vault they move packs. |

On the host, a pack vault looks like this:

```text
bare/packs/commits/    <epoch>__<commit id>__<bytes>.zip    one per push
bare/packs/snapshots/  <epoch>__<commit id>__<bytes>.zip    the first push and each compaction
bare/packs/archive/    the same names, moved there by compaction; never deleted
bare/refs/, bare/indexes/, bare/keys/                       exactly as on a normal vault
bare/data/                                                  empty, except tag objects
```

## 3. What it measured

Each pair is the same content as a normal vault and as a pack vault, on the same server (`dev.send.sgraph.ai`), from a cloud sandbox. Medians of three runs unless one number is given.

| | Normal vault | Pack vault |
|---|---|---|
| **A published vault:** 17 commits, 699 files, 2,087 objects (the [AIUC-1 conformance vault](https://sgit.ai/demos/vaults/index.html)) | | |
| Clone | 28.6 s | **8.1 s**, 4 requests |
| First push | 27.3 s | **11.8 s** |
| Push of one file | 10.5 s | **5.8 s** |
| Pull, 3 pushes behind | 4.8 s | 4.2 s |
| Stored file contents | 213 MB | **129 MB** (1.66×) |
| **A synthetic vault:** 30 commits, 300 prose and JSON files | | |
| Clone | 5.5 s | **3.3 s**, 3 requests |
| Push of one commit | 7.3 s | **5.3 s** |
| Pull, 5 pushes behind | 5.9 s | **3.6 s** |
| Stored file contents | 1.0 MB | **0.3 MB** (3.67×) |
| **The comms vault's history:** 1,229 commits, 33,000 objects, measured by the CLI team | | |
| Full clone | 3½ min | **25 s** (18 s of it one 251 MB download in 4 requests) |

Re-measured with the 0.24.0 wheel from PyPI after the release, on 22 October: the published vault cloned in 9.0, 9.3 and 9.8 seconds (7.2 s of each was the download, in 4 requests), and imported in about 9 seconds locally. That is within the spread between runs on the same day; the network accounts for it, not the code.

Two things the table does not show:
- **Pulls gain least.** Their time is the local merge and status walks, which are the same in both modes and are the CLI team's next target.
- **After a compaction, a clone that was behind downloads the whole snapshot** on its next pull: 130 MB and 9.5 s on the AIUC vault. Archived commit packs are never read by a pull.

## 4. Compatibility

- **Older clients are refused by name.** A pack vault's index carries `min_client = 0.24.0`. Checked live: sgit-ai 0.23.0 from PyPI says `this vault needs sgit-ai >= 0.24.0 and this is 0.23.0: run sgit update, then try again`. Clients older than 0.18.1 do not read `min_client` at all and would see an empty vault; that was already the case for any gated vault.
- **No web view.** The browser does not read packs. A vault that must be browsable on vault.sgraph.ai stays a normal vault, or comes back as one through `sgit pack export`.
- **`sgit clone` works in every form** (full, `--path`, `--depth`, read-only), but `--path` and `--depth` take the packs whole in this version. A scoped clone of one folder of a big pack vault is therefore a full download.
- **`sgit clone-headless` works:** its `fetch` takes the packs. `sgit clone-branch` and `sgit clone-range` refuse a pack vault with a sentence that says so.
- **Tags work.** Tag objects are the one thing still written loose to `bare/data/`; `pack stats` counts them separately.

## 5. Changes every vault gets

- **Large downloads read in parallel.** A presigned download (large files, large packs) reads in 8 MB ranges, 8 at a time. The CLI team measured 1.3 MB/s for one stream from a cloud sandbox and 11.8 MB/s for eight. Every range's length is checked, with one retry and then an error. A host that ignores `Range` is read in one stream as before.
- **A first push sends its refs last and on their own,** after the objects, keys and index. A first push that stops part-way is a first push again when it is retried, and never leaves refs naming objects that are not there.

## 6. Security

What the host learns from a pack vault:
- **From pack names and zip directories:** when each push happened, which commit it carried, and the sizes of its objects. This is the cost of the listing being the index (threat model row TM-R38).
- **With compression on:** how compressible each file is (TM-R40). `sgit pack import --no-deflate` makes a pack vault without compression. `init --packs` always compresses.

A pack cannot write anything a loose object could not:
- every member must be named `bare/data/obj-cas-imm-<hex>`, be stored uncompressed, and declare no more bytes than the pack holds, or it is refused by its directory entry without being read;
- a pack that names a member twice is refused whole;
- every member is checked against its content address before it is written;
- a forged pack cannot move the head, because the ref still moves only by compare-and-swap.

The feature was reviewed before release in four rounds by cli.sgit.ai's build agent, with tests, a code review and live trials. The rounds found four ways compaction could leave a fresh clone without part of the history (two in the first build, two in the fixes for them), a failed first push that could drop the root commit, a zip-bomb path, a gate that admitted older clients, and smaller issues. Each was fixed with a test. How that went is in [Four rounds to no blockers](/articles/pack-mode-four-rounds.html); the reports and the CLI team's answers are under [research](/research/topics/write-path.html).

## 7. Moving an existing vault

You do not convert a vault in place. You make a new pack vault from a full clone of it, and keep the old one:

```text
$ sgit clone <old vault key> old-full            # a full clone: no --path, no --depth
$ sgit pack import old-full new-packs            # prints the NEW vault key: save it
$ cd new-packs && sgit status                    # "This vault has never been pushed"
$ sgit push                                      # one snapshot
```

- **The new vault goes to the same server as the source.** To put it somewhere else, pass `--base-url` to the import, or run `sgit remote add origin <url>` in the new folder before pushing.
- **Hand out the new key.** Then retire the old vault when nobody uses it.
- **To go back,** `sgit pack export <pack clone> <new dir>` makes a normal vault again, with its own key. The round trip was tested end to end: identical files, the same commit messages, every signature verified.

## 8. Known limits

- No web view of a pack vault.
- `--path` and `--depth` take the packs whole; scoped reads of a snapshot are the next version.
- `clone-branch` and `clone-range` do not read packs yet.
- Compaction is manual (`sgit pack compact`). Nothing triggers it automatically. Run it when `commits/` holds more than about 50 packs, or more than a tenth of the snapshot's bytes.
- A clone that was behind when a compaction ran downloads the whole snapshot on its next pull.

*Sources: the CLI's CHANGELOG and its [pack-mode feature reference](https://github.com/SGit-AI/SGit-AI__CLI/tree/dev/team/humans/dinis_cruz/claude-code-web/10/22) (22 October 2026); the measurements are cli.sgit.ai's live trials of 21 and 22 October 2026 on dev.send.sgraph.ai, except the comms vault's, which are the CLI team's. Every claim in sections 4 and 6 was checked against the code at the merge to main (`ab97e497`) and on dev at `182cfc16`, and the release itself (`70b37483`, sgit-ai 0.24.0 from PyPI) was run through the playbook's recipes live on dev the evening it was published.*
