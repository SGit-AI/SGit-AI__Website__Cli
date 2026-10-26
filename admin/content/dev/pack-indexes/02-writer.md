---
title: Pack indexes, 02: the writer
summary: What push, compaction and pack import write, computed from what the writer already holds (the flat cache, the incremental build's changed paths, the parents); the order of uploads and what a failure leaves; the offset table; a new sgit pack index command for backfill, verification and stats; the cost budget; and the functions to change.
section: devpacks
order: 12
---

# 02. The writer

The rule: **the client that pushes pays, once, from what it already holds.** Nothing here may make a push read a tree it did not already read to build the commit.

## 1. At push: a commit index per commit pack

`Vault__Packs.push_packs` builds one data pack per commit (`build_commit_pack`) and uploads it to `commits/`. After each data pack is built, the writer also builds that commit's index pack:

1. **The changes.** The incremental tree build that made the commit (0.25.0) knows which paths it changed. Compare the parent's flat map (the flat cache) with the new head's, but only for those paths, and write `A`, `M` and `D` entries with the new blobs' `size`, `content_hash`, `content_type` and `large`. A merge commit is diffed against its first parent, which the merge also computed.
2. **The generation.** 1 + the highest generation of the parents, read from the local index (03). If a parent's generation is unknown, because the history predates indexes, compute it once by walking the local commit graph. The commits are local in a pack clone. Then record it.
3. **The folders.** Write a `folder:<path>` member for every folder whose tree id changed. These are exactly the trees the commit wrote, on the changed paths: 27 members for five files in the benchmark vault. `totals` come from the parent's member plus the change. `files` and `dirs` are the new tree's entries.
4. **The offsets (Phase 2).** `write_pack` returns each member's data offset (`header_offset + 30 + len(name)`, since the writer sets no extra field). Unchanged files keep the `at` of the parent's member, and the header's `data_packs` lists every pack those refer to.
5. **The header.** Lay out the members (section 4), sign the canonical header with the clone key used for commits, encrypt, pad, write.

**Order of uploads:** the data pack, then the index pack, then `record_absorbed` as today.
- **An index pack without its data pack** is ignored by readers (03). A push that dies between the two leaves a data pack without an index: a gap, which readers survive.
- **The ref moves only after both,** so a reader that sees the new head finds its index whenever the writer is new.
- **A failed index upload must not fail the push.** Warn, record the gap in `.sg_vault/local/index/gaps.json`, and retry it on the next push or `sgit pack index build`.

**Measured budget** for a five-file commit on the benchmark vault: about 10 ms to compute 38 members, and 0.92 s for 1,000 such commits. Target: under 1% of a push.

## 2. At compaction: the snapshot index

`Vault__Pack_Maintain.compact` writes a snapshot data pack for the head. Beside it, the writer writes the snapshot index:

| Member | Built from |
|---|---|
| `flat` | the head's flat map, from the flat cache, which the compacting client already has |
| `folder:*` | the flat map's `dirs`, grouped, with `totals` rolled up deepest-first, in 1.6 s for 58,062 folders |
| `commits:<n>`, `commit-gen` | `reachable_commits` (already called by compaction) with generations |
| `blob-paths:<xx>` | the flat map inverted |
| `file-commits:<xx>` | the previous snapshot index's `file-commits` plus the `changes` of every commit index this compaction absorbs; without a previous snapshot index, by diffing the absorbed history once |

**When compaction moves commit packs to `archive/`, it moves their index packs to `indexes/archive/`** under the same rules: copy, verify, then delete the original, as `_move_to_archive` does. An index pack whose data pack is gone from both `commits/` and `archive/` may be deleted.

The measured full build on the benchmark vault was 3.5 s, plus 1 s to write the zip. Compaction already writes a 69 MB data pack for that vault, so the index is a small share of it.

## 3. At `pack import`, `pack convert` and a first push

- **`sgit pack import`** (loose to packs) and `Vault__Pack_Convert` write a snapshot data pack. They write its snapshot index too.
- **The first push of a new pack vault** (`push_snapshot`) writes the snapshot index beside it.
- **The branch index gains the advisory feature `pack-indexes`** the first time a writer uploads an index pack. It never raises `min_client`.

## 4. The offset table

The header lists every member's offset. Its own size moves those offsets, so in the prototype a fixed-point iteration oscillated by 113 bytes and never settled. Instead:

1. Serialise and deflate every other member, and keep their lengths.
2. Compute offsets assuming the header member is `R` bytes, with `R = ceil((12 + estimate + 4096) / 16384) · 16384`. The estimate is the envelope length of the header with offsets at their maximum width.
3. Build, deflate and encrypt the header. Assert `12 + L ≤ R`. If not, double `R` and redo step 2.
4. Write member 0 padded to `R`, then the others in order.

This is measured on the benchmark vault's 58,598-member index: the table is 709 KB, and a reader opens the pack in 50 ms against 910 ms through the zip's central directory.

## 5. `sgit pack index`: new subcommands

| Command | What it does |
|---|---|
| `sgit pack index build [--all]` | writes the index pack of every data pack that has none: the gaps left by older clients or failed uploads. It needs the write key; any member with write access may run it. `--all` rebuilds the snapshot index too |
| `sgit pack index verify` | for every index pack: header signature, member hashes, `tree_id` against the commit, `flat` against a full tree walk, every `changes` against a tree diff, `folder:*` against its tree. Read-only; reports and exits non-zero on a mismatch |
| `sgit pack index stats` | index packs per folder, sizes, gaps, the newest snapshot index, generations covered |

`pack stats` and `pack ls` gain an index column.

## 6. Functions to change

| Where | Change |
|---|---|
| `Vault__Packs.write_pack` | accept an ordered id list (Phase 2), keep order while removing duplicates, return `{id: (offset, length)}` |
| `Vault__Packs.build_commit_pack`, `build_snapshot_pack` | pass the path order; return the offsets |
| `Vault__Packs.push_packs`, `push_snapshot` | build and upload the index pack after each data pack; record gaps |
| `Vault__Pack_Maintain.compact`, `_move_to_archive` | write the snapshot index; archive index packs with their data packs |
| `Vault__Pack_Convert.convert` | write the snapshot index |
| `Vault__Format` | add `FEATURE_PACK_INDEXES = 'pack-indexes'` to `KNOWN_FEATURES`, **not** to `FEATURE_MIN_CLIENT` |
| new `Vault__Pack_Index` (`sgit_ai/core/actions/pack/`) | build members, lay out, sign, encrypt, write; read header and members; verify |
| new `Schema__Pack_Index__Header`, `__Folder`, `__Changes` (Type_Safe) | the writer builds through these, so a wrong type fails at write time; readers load the JSON as dicts |
| `CLI__Pack` | the `index` subcommands |

## 7. What the writer must never do

- **Write an index that disagrees with the trees it pushes.** Build the index from the same in-memory maps the tree build used, never from the working copy.
- **Put a path, a name or a message in clear anywhere.** Member names are sequence numbers, and everything else is encrypted.
- **Make an index upload's failure fail the push.** A gap is a slower read, never a lost write.
