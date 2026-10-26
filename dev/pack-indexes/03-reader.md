# Pack indexes, 03: the reader, cli.sgit.ai

> How a reader finds index packs, verifies them and keeps them encrypted on disk; the local assembly (a snapshot index, the deltas over it, the newest version of each member, cross-references kept current from change lists); and what each command reads instead of walking: clone, clone --path, pull, history log, merge base, and reads without a clone. Gaps and every fallback.

*Source: <https://cli.sgit.ai/dev/pack-indexes/03-reader.html> · generated from the same content as the page, so the two cannot drift.*

---
# 03. The reader

## 1. Finding index packs

A pull or clone already lists `bare/packs/commits/` and `bare/packs/snapshots/` (`Vault__Packs.sync_down`). When the branch index has the feature `pack-indexes`, it also lists `bare/packs/indexes/commits/` and `bare/packs/indexes/snapshots/`. That is two more list requests, made only on vaults that have index packs.

Pair each index pack with its data pack by (folder, epoch, commit id). An index pack whose data pack is in neither its folder nor `archive/` is ignored.

**Download:**
- the snapshot index of the snapshot the clone takes;
- the commit index of every commit pack not yet absorbed;
- nothing from `indexes/archive/`, except when a clone takes an archived history.

Index packs are small (01, section 5), so they go through the batch read with the data packs.

## 2. Verifying an index pack

In order, before anything uses it:

1. **The header.** Magic and format byte; envelope decrypts under the read key; `schema` known.
2. **The signature.** Verify with the key named by `author_key_id` (`bare/keys/<id>`), by the vault's commit policy:
   - under `signatures-required`, a missing or bad signature means **ignore the index pack**;
   - otherwise an unsigned index is accepted, subject to step 3.
3. **The anchor.** `commit_id`, `parents`, `tree_id` and `timestamp_ms` must equal the commit object's, which the data pack carries and is verified by its id. For a snapshot, the root of `flat` must equal `tree_id`, and the root folder member's entries must equal the root tree's.
4. **Each member, when it is first read.** Decrypt, inflate, and check its SHA-256 against the header's.

A failure at any step drops that index pack: **the reader walks instead, for that pack only,** and reports it once (`sgit pack index verify` gives the detail). Nothing an index says is ever written to the working copy or the object store without the object it names verifying by its content address. That is today's rule for pack members, unchanged.

## 3. The local index

```
.sg_vault/local/index/
  packs/<folder>/<name>.zip     the index packs, as downloaded: encrypted
  state.json                    {schema, snapshot: name, deltas: [names, oldest first], gaps: [commit ids]}
```

- **Index packs stay encrypted on disk.** A member is decrypted when it is read, at about a microsecond per KB. This adds nothing in clear beyond what 0.25.0's flat and scan caches already hold, and it stays compatible with [sealed vault keys](../../dev/sealed-vault-keys/index.md).
- **The assembly is in memory, per process.** It is cheap enough to redo per process (section 4), so nothing assembled has to be written. A later optimisation may cache it under the same rules as the flat cache.
- **`state.json` is reset by a new snapshot.** When compaction makes a new snapshot index, the deltas start over.

## 4. Assembling

The local index answers four kinds of question. Each has its own structure, built on first use:

| Structure | Built from | Cost measured |
|---|---|---|
| **newest member:** logical name → the newest index pack holding it | the deltas' headers, newest wins, then the snapshot's | 6.6 ms for 1,000 deltas (10,620 names); a read through it 8 µs |
| **flat map of the head** | the snapshot's `flat`, then each delta's `changes` applied in order | 0.58 s to load 76,000 entries; applying a delta is a dict update per change |
| **commit graph:** id → parents, generation, time | the snapshot's `commits:*` loaded on demand through `commit-gen`, plus each delta's header | a merge base loaded 3 members |
| **cross-references:** blob → paths, path → commits | the snapshot's shards, then every delta's `changes` | 155 ms from the snapshot; 49 ms to apply 1,000 change lists |

**A gap** is a commit pack without a usable index. Compute its delta locally, which is what today's code does anyway: diff its tree against its first parent's, and take parents and generation from its commit object. Then carry on. A clone with gaps is as correct as one without, and only as slow as today for those commits.

## 5. Command by command

### `pull`

| Step | Today | With the index |
|---|---|---|
| new commits, base..head | walk of history (day-window bound on the branch) | the deltas' headers and the commit graph: generation walk, **0.1 ms** measured on 20,003 commits |
| merge base | walk | generation walk (git's paint-down: newest generation first, stop when every queued commit is reachable from both) |
| which objects are missing | `exists` over every id of the head: 6 s at 235,000 | the new blobs named by the new deltas' `changes`, checked against the local store |
| the new head's flat map | copy unchanged folders, read changed trees | the cached map plus the `changes`: no tree read |
| merge, three-way | changed paths, from tree diffs | changed paths from both sides' `changes` |

The dirty-tree check (the stat pass) and writing the changed files do not change.

### `clone` (full)

- Take the snapshot index with the snapshot data pack. Seed the flat cache from `flat` plus the deltas; that is no tree walk, where today the clone flattens after extraction.
- Seed the commit graph from `commits:*`.
- Extract the working copy as today. Phase 3 changes the object writes (section 6).

### `clone --path <folder>` and a scoped `pull` (Phase 2)

1. List; download the snapshot index and the commit indexes.
2. Find `folder:<folder>`: the newest version of it and of every folder below it, walking `dirs`. Measured: 1,161 members for a subtree of 1,520 files, in 36.5 ms. `totals` gives the size before anything is downloaded.
3. Collect the `at` of every file and `tree_at` of every folder in the scope, plus the trees on the spine from the root, which `Vault__Scope` needs to commit later. Group by data pack and merge ranges less than 64 KB apart.
4. Take each range with `fetch_presigned_range` when the host has presigned reads. Otherwise, and for a pack under `PACK_BATCH_MAX`, take the whole pack as today.
5. Verify every object by its id, write the scope, and record the scope as today.

Measured on the benchmark vault, with blobs in path order: one folder of 1,520 files was **1 range of 0.22 MB**. In today's id order the same blobs were 265 ranges over 30.4 MB, and today's clone takes the whole pack.

### `history log`, `log --stat`, `diff <a> <b>`

- **`history log`** reads the `changes` of each commit in the range; its counts come from the lists. No tree is opened. `log --stat` is the same.
- **`diff <a> <b>`** for commits on one line of history is the union of their `changes`. Otherwise it is two flat maps, as today.
- **A path's history** (`history log -- <path>`) is `file-commits` plus the newer deltas.

### `status`, `commit`, `push`

Unchanged for the reader. `push` does the writer's work (02).

### A read without a clone (Phase 4)

`sgit cat <vault> <path>`:
- list;
- download the snapshot index and the commit indexes, a few MB;
- the newest `folder:<parent of path>` gives the blob's `at`;
- one ranged read, verify, decrypt.

That is three or four requests, whatever the size of the vault.

## 6. The pack as the store (Phase 3)

This is the CLI team's architecture, phase 1, unchanged in substance and listed here for completeness. A pack clone keeps the data packs it downloads under `.sg_vault/bare/packs/`, and the object store reads a member by offset. Offsets come from each pack's central directory, read once per pack: 0.56 s for 134,092 members. With Phase 2, the folder members' `at` give them too.

- **Verification moves to the first read** of each object, and the verdict is remembered.
- **Loose objects win over packed ones;** a clone's own new objects stay loose until pushed.
- **Measured:** 5 µs per read in place, against 11.6 s to write every object of the benchmark vault loose, and many minutes on a slow disk.

## 7. Fallbacks, all of them

| Situation | The reader does |
|---|---|
| no `pack-indexes` feature | today's code, no index listing |
| an index pack fails verification | ignore it; walk for that pack |
| a commit pack has no index (gap) | compute that delta locally; continue |
| an unknown `schema` or format byte | ignore the index pack |
| the snapshot index is missing | build the snapshot structures by walking, as today; deltas still apply on top |
| a ranged read is refused (no presigned route) | take the whole pack |
| an object named by an index fails its id | refuse it as today, and drop that index pack for the rest of the command |

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/dev/pack-indexes/03-reader.html)*
