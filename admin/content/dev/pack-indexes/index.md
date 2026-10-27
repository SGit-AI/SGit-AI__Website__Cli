---
title: Pack indexes for sgit: a design pack
summary: An implementation spec for the sgit CLI team. The client that pushes a pack also pushes an index pack beside it, encrypted and signed. A snapshot's index holds the head's flat map, one file per folder, the commit graph with generation numbers, and cross-references. A commit's index is a delta: the folder files on the changed paths and a change list. Readers assemble them locally and stop walking trees, unpacking objects they do not read, and downloading folders they do not want. Clients up to 0.25.0 never see index packs. Expected impact per command, the formats, the writer, the reader, compatibility, the threat model, the phases and the acceptance tests.
section: devpacks
order: 10
---

# Pack indexes for sgit: a design pack

> **Shipped, 27 October 2026.** Phases 1 to 3 of this pack, with a selective working copy the CLI team added, shipped in **sgit-ai 0.26.0**: [the release notes](/docs/update-to-0-26-0.html), and [the story, the reviews and the measurements](/articles/pack-indexes-shipped.html). Phase 4, reading a file with no clone, is not built. The text below is the design as written.

**Status:** design, 26 October 2026, for the sgit CLI team. Nothing here was built when it was written. It is written against SGit-AI__CLI at `c0694753` (branch `claude/charming-babbage-5hzcxq`, after 0.25.0) and the code names below are from that commit.

**Compatibility is a requirement.**
- A vault with index packs works unchanged for every client from 0.24.0 to 0.25.0. They never list the folder the index packs live in.
- No `min_client` rises.
- A vault without index packs works unchanged for new clients, which fall back to today's walks.

**Audience:** the agents and engineers who will build this. Read in order.

| # | Document | What it settles |
|---|---|---|
| 00 | this file | the problem, what it buys per command, the principles, the decisions, the phases |
| 01 | [01-format.md](/dev/pack-indexes/01-format.html) | where index packs live, the zip layout, the encrypted header, every member's JSON schema, data packs in path order |
| 02 | [02-writer.md](/dev/pack-indexes/02-writer.html) | what push, compaction, `pack import` and a new `sgit pack index` command write, from what the writer already holds |
| 03 | [03-reader.md](/dev/pack-indexes/03-reader.html) | discovery, verification, the local assembly, and what each command reads instead of walking |
| 04 | [04-compatibility-security-and-tests.md](/dev/pack-indexes/04-compatibility-security-and-tests.html) | old and mixed clients, the threat model, the phases with acceptance tests and benchmarks, open questions |

**Where the evidence is:** four articles and a research record on this site, all of 26 October 2026, measured on the 76,000-file benchmark vault and on synthetic data. Every script is in this site's repository.
- [Indexes in the pack](/articles/indexes-in-the-pack.html): the flat index, packs read in place, path-ordered ranges, and the correction that a 0.25.0 client re-downloads a pack with an unknown member.
- [A vault is already a graph](/articles/a-vault-is-already-a-graph.html): nine engines, and generation numbers.
- [Indexes the writer pays for](/articles/indexes-the-writer-pays-for.html): the principles, the per-folder layout, the offset table, the million-page test, the deltas.
- [Graph and index measurements](/research/graph-and-index-measurements-2026-10-26.html): every number.
- The CLI team's own [architecture](/research/pack-carried-indexes-architecture.html) and [review of indexes and caches](/research/indexes-and-caches-review.html). This pack builds on both and changes three of their decisions (section 5).

---

## 1. The problem

0.25.0 made local commands follow the size of the change. What still follows the size of the vault, on a pack vault, is everything a reader has to **recompute or download** that the writer already knew:

| Cost today | Measured | Why |
|---|---|---|
| A clone writes every object loose before anyone can work | 305,230 object writes on the CLI team's 228,000-file vault (clone 216 s); 11.6 s for 134,092 objects on a fast disk here; on a cloud session's disk the curator's first command waited 17 minutes | `extract_pack` unpacks every member into `bare/data/` |
| A partial clone of a pack vault is not partial on the wire | the newsroom's 1.22 GB snapshot to read one folder | `Step__Clone__Bulk_Fetch.pack_vault_fetch`: "a partial clone (--path/--depth) still takes the packs whole" |
| A pull's commit list and merge base walk history | about 0.4 ms per commit of history (1.9 s on 5,000); the branch bounds it by a day of clock skew | no generation numbers anywhere |
| `history log` diffs trees | 7.4 s for 10 commits on the 228,000-file vault | each commit's change is recomputed by walking where tree ids differ |
| A pull of a pass checks every blob for presence | 6 s of the 31.7 s pull on the branch (`exists` over 235,000 ids) | no list of what the new commits added |
| The first flatten of a head this clone has never seen | about 45 s full; the branch copies unchanged folders and reads changed trees | the writer had the map and did not send it |

**What is not in scope:** the stat pass of `status` (4 s at 76,000 files, 15 s at 228,000), writing the working files a working clone needs, and the bandwidth of a full clone. Indexes do not remove those.

## 2. What it buys, command by command

Expected, not measured in sgit: each "after" is a prototype measurement on this site or a direct consequence of removing a step that was measured.

| Command, pack vault | Today | After | Phase |
|---|---|---|---|
| `pull`: list of new commits, merge base | walk of history, up to seconds | **0.1 ms** each with generation numbers (prototype, 20,003 commits) | 1 |
| `history log`, 10 commits with counts | 7.4 s (228,000 files) | **milliseconds**: read 10 change lists | 1 |
| `pull`: which blobs are missing | 6 s | a set built from the change lists: **milliseconds** | 1 |
| `pull`: new head's flat map | walk of changed folders | apply the change list to the cached map: **milliseconds** | 1 |
| First command after a clone | flat map from a walk, or seeded by the clone | seeded from the snapshot's `flat` member: **0.58 s** to read 76,000 entries | 1 |
| `clone --path <folder>` | the whole snapshot and every commit pack | the index packs, then **one ranged read per folder** (1,520 files: 0.22 MB in one range, against 30.4 MB in 265 ranges in id order) | 2 |
| `clone` (full) | download, 305,230 object writes, 228,000 file writes | download, 228,000 file writes; objects read from the packs in place (5 µs each) | 3 |
| One file, no clone | a clone | the index packs, then **one ranged read** | 4 |
| `status`, `commit` | unchanged | unchanged | none |

**The largest gains** are for readers that want part of a vault (gigabytes become megabytes), for history questions (seconds become milliseconds), and for clones on slow disks (Phase 3). For a working clone that touches every file, the working copy itself remains the cost.

## 3. The principles

Dinis Cruz's, tested in [Indexes the writer pays for](/articles/indexes-the-writer-pays-for.html#principles):

1. **The writer pays.** The client that pushes computes the indexes once. It already holds the answers: its flat cache, the changed paths, the parents.
2. **Cross-reference in both directions,** so a reader goes from any id to everything that points to it.
3. **One index per question,** sharded the way that question walks: commits by generation, folders by path, blobs by id.
4. **Plain JSON, typed at the writer.** The writer builds through Type_Safe schemas; the reader loads JSON as dicts. No database file travels.
5. **Load on demand** from the zip, one member at a time, located by an offset table the writer stores.
6. **One file per folder,** rewritten on the paths a commit changes, as trees already are.

And one rule from the CLI team's architecture, kept unchanged: **an index is a plan, never a proof.** Every object is verified by its content address before it is used. Lose every index and nothing is lost.

## 4. Glossary

| Term | Meaning |
|---|---|
| data pack | a pack as in 0.24.0: `bare/packs/{commits,snapshots,archive}/<epoch>__<commit>__<bytes>.zip`, members `bare/data/<object id>` |
| index pack | a zip beside a data pack, under `bare/packs/indexes/`, with the same name, holding encrypted index members (01) |
| snapshot index | the index pack of a snapshot data pack: the whole head and its history |
| commit index | the index pack of a commit data pack: a delta, the folder files on the changed paths and a change list |
| member | one encrypted JSON document inside an index pack, found through the header |
| header | the first member of an index pack: the encrypted, signed table of every other member |
| generation | 1 + the highest generation of a commit's parents; 1 for a root |
| local index | the index packs a clone keeps under `.sg_vault/local/index/`, and what it assembles from them (03) |

## 5. Decisions

| # | Decision | Why | Changes from the CLI architecture |
|---|---|---|---|
| D1 | Index packs live in **`bare/packs/indexes/{commits,snapshots,archive}/`**, never inside a data pack | 0.24.0 to 0.25.0 refuse an unknown member in a data pack and **re-download that pack on every pull** (tested on 0.25.0 from PyPI). They list only `bare/packs/commits/` and `bare/packs/snapshots/`, so they never see index packs | yes: the architecture put `bare/index/*` members in the data pack and gated it |
| D2 | **No `min_client` change.** An advisory feature `pack-indexes` in the branch index says "writers here produce index packs" | unknown features are ignored by 0.24.0 to 0.25.0 (`Vault__Format.gate_this_build_carries`, `check_client`) while `min_client` stays | yes: no gate |
| D3 | Members are **JSON, deflated, then encrypted** with the read key (`Vault__Crypto.encrypt`), one AES-GCM envelope each | JSON-native; same primitive as trees; no database file to trust | no |
| D4 | Member names in the zip are **opaque sequence numbers**; their meaning is only in the encrypted header | the host learns nothing from names: not paths, not which object is a tree, not which folder changed | refines: no keyed names needed |
| D5 | The header is **signed by the pusher's clone key** over its canonical JSON, which lists every member's plaintext SHA-256 | the index gets exactly the standing of the commit it describes | same intent |
| D6 | A snapshot index carries **`flat`, `folder:*`, `commits:*`, `commit-gen`, `blob-paths:*`, `file-commits:*`**; a commit index carries **`changes`** and the **`folder:*`** members on the changed paths | the snapshot answers every question; a delta costs 3.1 KB for a five-file commit, against 47.7 KB when shards travel | refines `flat/`, `diff/`, `graph/` |
| D7 | **Generation numbers live in index members, not in commits** | `commit_v1` has no field for it, and a commit-schema change would be a gate | yes: the architecture proposed them in `graph/` members, same idea |
| D8 | New data packs store members in **path order**: commits, then trees by path, then blobs by the path of their first use | one folder becomes one contiguous range; the order is a function of the tree, so packs stay deterministic; `pack verify` and old readers ignore order | new |
| D9 | `folder:*` members carry each blob's **`at`: data pack, offset, length** | a scoped reader never parses a data pack's central directory (10.7 MB for 134,092 members) | new |
| D10 | **Missing or bad indexes fall back to today's walks**, per pack | mixed writers (0.25.0 pushing to an indexed vault) leave gaps; a reader must never depend on an index existing | same |
| D11 | Readers keep index packs **encrypted on disk** and decrypt members on read | nothing new in clear on disk, compatible with sealed vault keys; decryption is about a microsecond per KB | yes: the architecture assembled into SQLite on disk |
| D12 | **No SQLite, no graph engine, no new dependency.** Dicts and the standard library | measured: dictionaries answered every question fastest; databases added load time | yes: SQLite was the architecture's local form |

## 6. Phases

| Phase | What | Removes | Size |
|---|---|---|---|
| **1** | Index packs: writer at push, compaction, `pack import`; `sgit pack index build/verify/stats`; reader for pull (commit list, merge base, missing blobs, new flat map), `history log`, first flatten after clone | the history walks and the per-blob presence check; the first full flatten | 4 to 5 days with tests |
| **2** | Path-ordered data packs with `at` offsets; `clone --path` and scoped `pull` on pack vaults by ranged reads | the whole-pack download for partial clones | 3 days |
| **3** | The pack as the store: keep packs, read in place, verify on first read (the CLI architecture's phase 1) | the 305,230 object writes of a clone | 3 days |
| **4** | Readers without a clone: `sgit cat`/`fetch` of a path from the index packs and one ranged read | the clone itself, for readers | with the SG/Vault team |

Phase 1 is independent of 2 and 3, and has the widest effect. Phase 3 is local only and can run in parallel. Each phase ends with its acceptance tests (04) green and its benchmark run on the 76,000-file vault and the 228,000-file synthetic vault.
