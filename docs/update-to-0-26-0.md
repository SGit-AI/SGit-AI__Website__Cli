# sgit-ai 0.26.0 release notes: pack indexes, selective working copies, the pack store, cli.sgit.ai

> Release notes for sgit-ai 0.26.0, for people and agents. Every push to a pack vault now writes an index pack beside its data pack, so readers stop walking trees. A pull plans its fetch from the indexes, and history log reads change lists. A clone can skip writing the working copy, and an agent then checks out only the files it needs. A clone can keep the packs in place instead of unpacking hundreds of thousands of objects. A clone of one folder takes that folder by byte ranges. On a 76,000-file vault, a full clone fell from about two minutes to one, a no-checkout clone takes about 28 seconds, a one-folder clone under 3 seconds against 36, and history log half a second against three. The new agent loop, the commands, the compatibility rules (a pack vault created by 0.26.0 needs 0.26.0), what is on disk, and what is still slow. Nothing changes on the server.

*Source: <https://cli.sgit.ai/docs/update-to-0-26-0.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit-ai 0.26.0: pack indexes

The release notes for 0.26.0, written to be read by a person or handed to an agent.
- **Your daily loop does not change.** `clone`, `pull`, `status`, `commit` and `push` work as before.
- **Nothing changes on the server.**
- **On pack vaults, much of the work a reader used to redo is now done once by the writer and shipped beside the pack.** The new options below let an agent take only what it needs.

The design is the dev pack [Pack indexes for sgit](../dev/pack-indexes/index.md). The story and the numbers are in [Pack indexes, shipped](../articles/pack-indexes-shipped.md).

## 1. Update and check

```text
$ sgit update          # wraps: pip install --upgrade sgit-ai
$ sgit version
sgit-ai v0.26.0
```

If `sgit version` prints a note that another `sgit` comes first on your PATH, you have two installs. Upgrade that one too, or put this one first. Existing clones need nothing.

## 2. What is new

### Index packs: on by default, nothing to do

- **What a push writes.** Every push to a pack vault uploads, beside each data pack, an **index pack** under `bare/packs/indexes/`, encrypted with the read key and signed with your clone key. It holds:
  - the commit's change list;
  - the folders it changed;
  - its generation number.
- **What a snapshot index holds.** Each compaction writes one with the head's whole file map, one entry per folder, the commit graph and two cross-references (blob to paths, file to commits).
- **What readers do with them.** They use the indexes instead of walking trees:
  - a pull plans its fetch from them;
  - a fresh clone takes its file map from them;
  - `history log` reads its counts from the change lists, fetching the indexes of archived commits when it needs them.
- **Every answer is checked.** An index is checked against the commit, its signature and its trees before use, and every object it names is still verified by its id. A missing or bad index is skipped and the reader walks as before.

**For older pack vaults:** run this once, with the write key, to give them indexes:

```text
$ sgit pack index build     # writes the index packs the vault lacks, adds the 'pack-indexes' feature
$ sgit pack index verify    # checks every index against its trees (read-only)
$ sgit pack index stats
```

### A selective working copy: the loop for agents that do not need every file

```text
$ sgit clone --no-checkout <vault key> work      # the vault's objects and index, no files written
$ cd work
$ sgit checkout sources/uk                       # write a folder (or files) you need
$ ... read, write, add files ...
$ sgit commit -m "..." && sgit push
$ sgit pull --no-checkout                        # move the head; list what changed; write nothing
$ sgit checkout --since-pull                     # write what that pull added or changed
```

- **What `status` and `commit` count.** A file never checked out is **not** a deletion. A checked-out file you delete is one. The record is `.sg_vault/local/checkout.json`; if it is lost, sgit rebuilds it from the files on disk.
- **`sgit checkout` keeps your uncommitted edits.** A path you have changed is left alone and reported as `≠ path (kept: yours, uncommitted)` unless you pass `--force`.
- **Other ways to choose files:**
  - `sgit checkout --changed-since <commit>` writes what changed since that commit;
  - `sgit checkout --all` writes everything and makes the clone a full one, but only when every file could be written.
- **A plain `sgit pull`** on a selective clone writes only the changed files you have checked out. It lists the rest, for `sgit checkout --since-pull`.

### The pack store: `clone --pack-store`

```text
$ sgit clone --pack-store <vault key> work
```

- **What it does.** A pack clone keeps the packs it downloads under `.sg_vault/bare/packs/` and reads each object from its pack by offset. It no longer unpacks hundreds of thousands of objects into `bare/data/`.
- **Every read is verified.** Each object is checked against its id when it arrives and again every time it is read.
- **Managing it:**
  - `sgit pack store status` shows the kept packs;
  - `sgit pack store extract` turns the clone into an ordinary one;
  - `sgit pack store rebuild` recovers the offset table from the packs.
- **Do not open a `--pack-store` clone with 0.25.0.** It does not know the store. Run `sgit pack store extract` first if an older client must use the folder.

### One folder of a pack vault by byte ranges: `clone --path`

```text
$ sgit clone --path sources/uk <vault key> work
```

- **What travels.** A scoped clone of a pack vault reads only what the folder needs, by ranged reads from the packs on the host. 0.25.0 downloaded every pack whole.
- **Pack order.** Packs are now written in path order, so one folder's files sit together.
- **Hosts without ranged reads.** Where the host has no presigned route (`sgit serve`, a self-hosted server), the packs come whole, as before, and the clone says so.

### Also in this release

- **The newsroom's first-morning fixes:**
  - every file sgit writes (clone, pull, checkout, branch switch) is recorded in the scan cache, so the first `status` after a clone stats files instead of reading them back;
  - a pull of another clone's pass only walks what changed: 566 s → 31.7 s measured by the CLI team on 228,000 files;
  - `sgit version` names a shadowing install.
- **From the 0.25.0 review:**
  - `pull`'s list of new commits expands its base only within a day of clock skew;
  - Windows uses its change time in the scan cache key.

## 3. What it measured

The CLI team's release measurement: a synthetic vault of 76,000 files in 58,553 folders, built by each build under test, on an in-memory host, 4 cores. Network time is excluded.

| Flow | 0.25.0 | **0.26.0** |
|---|---|---|
| full clone | 117 s | **61 s** |
| `clone --no-checkout` | n/a | **28 s** |
| `clone --pack-store` | n/a | **26 s** |
| `clone --path` of one folder (1,520 files) | 36 s, the whole 88 MB pack | **2.8 s**, 12.5 MB by ranges |
| pull of a pass, full clone | 81 s | **6.6 s** |
| push of a 5-file commit | 6.2 s | **4.5 to 5.2 s** |
| push of a 300-file pass | 12.5 s | **11.6 to 11.8 s** |
| `history log`, 4 commits | 3.2 s | **0.45 s** |
| `history log` on a fresh clone after compaction | 6.1 s | **1.1 s** |
| first push of a new vault (snapshot) | 47 s | 82 to 84 s |
| compaction | 58 s | 95 to 109 s |

cli.sgit.ai measured the released code (`09172b0f`) independently on its own 76,000-file vault: full clone 49.8 s, `--no-checkout` 33.6 s, `--pack-store` 27.7 s, `clone --path` 3.1 s, a 5-file push 5.2 s, `pull --no-checkout` 1.1 s, `history log` 0.19 s, and 0.84 s on a fresh clone after compaction; [the table](../articles/pack-indexes-shipped.md#measured). Both sets agree: everything an agent does daily is as fast or faster. The first push of a vault and each compaction now also write the snapshot index, which is the price of the rest.

## 4. Compatibility

| Situation | What happens |
|---|---|
| **an existing pack vault, agents on 0.25.0 and 0.26.0 together** | works. 0.25.0 never reads `bare/packs/indexes/`; 0.26.0 fills the gaps 0.25.0's pushes leave. The vault's `min_client` does not change |
| **a pack vault created with 0.26.0** | **needs 0.26.0.** As since 0.24.0, a new pack vault is gated at the release that created it. Update every agent that will use it before you create it. [R3-2](../research/pack-indexes-review-round-3.md#r3-2) |
| **a `--pack-store` clone** | only 0.26.0 opens it; `sgit pack store extract` makes it an ordinary clone |
| **`sgit pack index verify` after a compaction of an older vault** | may report wrong offsets (`at`) in the index of an archived 0.24.0 or 0.25.0 pack; no data is affected and no reader in 0.26.0 uses those offsets. [R3-1](../research/pack-indexes-review-round-3.md#r3-1) |
| **normal (loose) vaults** | unchanged |

## 5. What is on disk now

Everything below lives under `.sg_vault/local/` in each clone, readable by you alone, as in 0.25.0:

| File | Holds | Delete it? |
|---|---|---|
| `index/packs/<folder>/<name>.zip` | the index packs this clone downloaded, **still encrypted** | safe; fetched again when needed |
| `index/cd/<folder>/<name>.json` | the central directories a scoped clone read (object ids and offsets) | safe |
| `checkout.json`, `last-pull.json`, `stale.json` | a selective clone's record: the paths checked out, what the last pull changed, bytes a pull left behind | safe; rebuilt from the files on disk |
| `pack-store.sqlite` | a `--pack-store` clone's table of where each object sits in which pack | safe; `sgit pack store rebuild` |
| `generations.json`, `gaps.json` | commit generations this clone computed; data packs it pushed without an index | safe |

The flat cache and scan cache of 0.25.0 are unchanged (threat model TM-R41). The index packs add nothing in clear: they stay encrypted on disk and are opened in memory.

## 6. Still slow, or not covered

- **The first push and each compaction** take 35 to 50 s longer on a 76,000-file vault, to build the snapshot index. It is 31.6 MB beside an 88 MB pack on that vault of small files, and a few per cent on vaults with real content. Making the cross-references optional is an open decision.
- **A full clone still writes every working file.** Use `--no-checkout` and `sgit checkout` for the folders you need.
- **`status` still stats every file** it tracks: about 4 s at 76,000 files.
- **Reading one file with no clone at all** (Phase 4) is not in this release.

*Sources: the CLI's CHANGELOG `[Unreleased]` section and the CLI team's documents of 26 and 27 October, published here as research: [the dev-pack review](../research/pack-indexes-dev-pack-review.md), [steps 1 to 5 shipped](../research/pack-indexes-steps-shipped.md), [their own review](../research/pack-indexes-cli-self-review.md), [the fixes](../research/pack-indexes-review-fixes.md) and [release readiness](../research/pack-indexes-release-readiness.md); cli.sgit.ai's reviews, rounds [1](../research/pack-indexes-review-round-1.md), [2](../research/pack-indexes-review-round-2.md) and [3](../research/pack-indexes-review-round-3.md), run against SGit-AI__CLI at `a9f24d86`, `58f52a42` and the dev merge `09172b0f`.*

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/update-to-0-26-0.html)*
