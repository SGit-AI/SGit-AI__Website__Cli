---
title: Pack indexes, 04: compatibility, security and tests
summary: How old, new and mixed clients behave on vaults with and without index packs; the threat model (a lying index, what the host learns, path order, what stays in clear locally); the rollout per phase; the acceptance tests and benchmarks each phase must pass; and the questions left open.
section: devpacks
order: 14
---

# 04. Compatibility, security and tests

## 1. Compatibility

| Client | Vault without index packs | Vault with index packs |
|---|---|---|
| 0.23.x and older | refused by the pack gate, as today | refused, as today; nothing changes |
| **0.24.0 to 0.25.0** | as today | **as today.** It never lists `bare/packs/indexes/`, ignores the advisory feature, extracts path-ordered packs (sorted by name before writing) and verifies them by hash. It pushes commit packs without indexes: gaps, which new readers fill locally |
| new, Phase 1+ | as today: no index listing without the feature | uses the indexes; walks across gaps |

**Acceptance test C1 must hold on every phase:** sgit-ai 0.25.0 from PyPI clones, pulls, pushes, compacts and runs `pack verify` on an indexed vault with output identical to an unindexed one. That includes not one extra request to `indexes/`.

**Loose vaults are untouched.** Indexes are a pack-vault feature; the cache layer (08/12) remains the loose vault's index.

## 2. Threat model

New rows for the threat model, beside TM-R41 (the 0.25.0 caches).

| Threat | What stops it | Residual |
|---|---|---|
| **The host** forges or alters an index member | AES-GCM under the read key; the header's member hashes; the signature | none beyond today: the host can delete, which is a gap |
| **The host** learns paths, names, messages or which objects are trees from index packs | everything is encrypted; member names are sequence numbers | sizes of index packs and members, and their count per commit, which already shows as the data pack's size |
| **The host** learns structure from path-ordered data packs (Phase 2) | it sees which members are adjacent, which shows blobs grouped by folder and roughly each folder's size, not names | **a new, mild leak.** Mitigations: order by top-level folder groups and by id inside each group; a per-vault option `pack-order: id` that keeps today's order and gives up ranged scoped reads. Record it as TM-R42 |
| **The host** learns what a reader reads, from its ranged reads | none, as today: per-object reads on loose vaults show the same | unchanged |
| **A write-key holder** pushes an index that disagrees with the trees | signature binds it to a key; under `signatures-required` the same policy as commits; the anchor check (root equals the commit's tree); every object still verified by id before use | a signing teammate can mislead a reader's plan (fetch the wrong set, show a wrong `log`), never what is written. `pack index verify` detects it in full |
| **A write-key holder** pushes an index whose `at` points at other bytes | the bytes must hash to the blob id the entry names | none: a mismatch is refused, the index dropped |
| **A local reader** of the disk learns more than today | index packs stay encrypted on disk; assembly is in memory | none beyond TM-R41 |
| **A crafted header** exhausts memory or time | header reserved size R at most 64 MiB; member length at most 256 MiB; JSON depth bounded; members checked against their hash before parsing | a large but honest index costs what it costs |

## 3. Rollout

| Stage | What | Who |
|---|---|---|
| 1 | Phase 1 behind `SGIT_PACK_INDEXES=1` for writers; readers use indexes when present | the CLI team, on test vaults and the benchmark vaults |
| 2 | writers on by default; `sgit pack index build` run once on the newsroom's vaults to backfill | the newsroom's agents, which upgrade on a brief |
| 3 | Phase 2: path-ordered packs from new pushes and compactions; `clone --path` uses ranges | after C1 and T7 pass on dev |
| 4 | Phase 3: pack store, behind `SGIT_PACK_STORE=1`, then default after the cloud-disk benchmark | the CLI team |
| 5 | Phase 4: reads without a clone | with the SG/Vault team |

**Rollback at any stage:** stop writing index packs. Readers fall back per pack; nothing on the host needs removing, and old clients never noticed.

## 4. Acceptance tests

Each phase ships with its tests green on the in-memory host and once live on dev.

| # | Test | Phase |
|---|---|---|
| **C1** | 0.25.0 from PyPI on an indexed vault: clone, pull, push, compact, `pack verify` give identical results and make no request under `indexes/` | every phase |
| T1 | **Index equals walk.** The fuzzer (16 seeds, about 450 commits, merges, deletes, renames): after every push, the flat map assembled from indexes equals a full tree flatten; every `changes` equals `diff_trees` of the commit against its first parent; every folder member equals its tree | 1 |
| T2 | **History.** base..head and merge base from generations equal a full walk, on the fuzzer's histories and on a history with a clock 1 day behind | 1 |
| T3 | **Gaps.** A 0.25.0 client pushes three commits into an indexed vault; a new reader's flat map, log and commit list equal a full walk, and `pack index build` fills the gaps | 1 |
| T4 | **A lying index.** For each: a changed blob id in `flat`, a wrong `tree_id`, a bad signature on a `signatures-required` vault, a member whose hash differs from the header, a truncated header. The index is dropped, the command succeeds by walking, and nothing wrong is written | 1 |
| T5 | **Orphans.** An index pack without its data pack is ignored; a data pack without an index is a gap | 1 |
| T6 | **Compaction.** After compaction, index packs of archived commit packs are in `indexes/archive/`; a fresh clone uses the snapshot index alone | 1 |
| T7 | **Scoped clone by ranges.** On the counted host, `clone --path raw/c09/s4` of the benchmark vault downloads at most the index packs plus 1.1 × the scope's bytes, and its working copy equals a full clone's folder | 2 |
| T8 | **Determinism.** The same commit gives the same data pack bytes, path-ordered; 0.25.0 extracts it identically | 2 |
| T9 | **Pack store.** A clone with the pack store and one without produce identical working copies and identical answers to `status`, `log` and `fsck`; one flipped byte in a kept pack is caught on first read | 3 |
| T10 | **Nothing new in clear.** After clone, pull and log, no file under `.sg_vault/` holds a path or name that 0.25.0 would not have held | 1 |

## 5. Benchmarks

Run before and after each phase, on the 76,000-file benchmark vault and the CLI team's 228,000-file synthetic vault, on the in-memory host and once against dev. Record them in the CHANGELOG.

| Benchmark | Today | Phase target |
|---|---|---|
| pull of a 300-file pass | 31.7 s (branch; 228,000 files) | Phase 1: the 6 s presence check and any tree reads gone; what remains is the stat pass and the file writes |
| `history log`, 10 commits with counts | 7.4 s (228,000 files) | Phase 1: under 100 ms |
| base..head on a 5,000-commit history | 1.9 s at 0.25.0 | Phase 1: under 1 ms after the index is loaded |
| first flatten of an unseen head | about 45 s (228,000 files) | Phase 1: under 2 s |
| `clone --path` of 1,520 files | the whole snapshot | Phase 2: index packs plus about 0.22 MB |
| full clone | 216 s (228,000 files) | Phase 3: the object writes gone; measure on a cloud session's disk |
| push of one five-file commit | as 0.25.0 | every phase: no more than 1% slower |

## 6. Open questions

1. **Path-order grouping.** Group by top-level folder (milder leak, coarser ranges) or full path order (one range per folder)? The recommendation is top-level groups by default, with full path order as a per-vault choice.
2. **`flat` and `folder:*` both in the snapshot.** `flat` serves full clones in one member; folders serve scoped readers. Both cost about 14 MB for the benchmark vault. Keep both until a measurement says otherwise.
3. **`file-commits` across a shallow boundary.** Stop at the boundary, as `Vault__Scope` does, and say so in the member.
4. **Index packs for loose vaults.** Not needed now: loose vaults are the small ones. Revisit if a large loose vault appears.
5. **Under sealed vault keys,** the local index is already encrypted at rest. The in-memory assembly lives in the process that holds the read key, so this needs nothing new.
