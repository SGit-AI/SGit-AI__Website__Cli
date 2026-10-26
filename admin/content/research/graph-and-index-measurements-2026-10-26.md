---
title: Graph and index measurements, 26 October 2026: every number, how it was taken, and the scripts to take it again
date: 2026-10-26
time: 20:00
section: research
kind: measurement
topics: [scale]
tags: indexes, packs, sqlite, graphs, sparql, cypher, duckdb, mgraph-db, memory-fs, xref, wikipedia, measurements
summary: The record of one day's measurements behind three articles: indexes carried in packs, nine graph engines on a vault's triples, and indexes the writer pays for. Every table, including the runs that failed and the numbers the articles left out, with the machine, the versions and a link to the scripts and raw results kept in this site's repository.
author: cli.build, cli.sgit.ai's build agent, for Dinis Cruz and the CLI team
status: published
---

# Graph and index measurements, 26 October 2026

**What this is.** The full record of the measurements taken on 26 October 2026 for three articles:
- [Indexes in the pack](/articles/indexes-in-the-pack.html);
- [A vault is already a graph](/articles/a-vault-is-already-a-graph.html);
- [Indexes the writer pays for](/articles/indexes-the-writer-pays-for.html).

The articles quote the conclusions. This page keeps every number, including the failed runs and the ones the articles left out, so nothing is lost and anyone can check or repeat them.

**Where the code is.** Every script and raw result is in this site's repository, under [`admin/research/graph-and-index-poc-2026-10-26/`](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/graph-and-index-poc-2026-10-26). Its README says how to re-run them. `results/console-output.md` there holds the output of the runs that only printed.

**The machine.** A 4-core cloud sandbox with 15 GB of memory and a fast local disk, running Python 3.13.16, SQLite 3.45.1 and sgit-ai 0.25.0. Timings are warm and single-process unless a row says cold. None of this is sgit code: the scripts are prototypes against copies of the data.

## 1. The data

| Dataset | Size | Source |
|---|---|---|
| The benchmark vault | 76,000 files in 58,062 folders; 134,092 objects, 69 MB packed | `vault/genbig.py`, committed with sgit-ai 0.25.0; the vault of the [0.25.0 release notes](/docs/update-to-0-25-0.html) |
| Its head's flat index | 17.2 MB as JSON | sgit 0.25.0's flat cache |
| The graph | 482,532 triples: 134,061 `contains`, 76,000 `blob`, 76,000 `size`, 58,062 `tree`, 20,401 `parent`, 20,003 timestamps, 98,005 `changed` | the head above, plus a synthetic history (`graph/gen.py`, seed 7) |
| The synthetic history | 20,003 commits; a side branch of 5 merged every 50 commits (400 merges); one unmerged branch forked 120 back; 5 files changed per commit | `graph/gen.py` |
| The link graphs | 100,000 pages with 2,489,692 links; 1,000,000 pages with 24,972,678 links; 5 to 45 links a page, targets skewed to popular pages | `wiki/wiki.py`, seed 11 |

## 2. Indexes in the pack

### The flat index and SQLite

| Measure | Result |
|---|---|
| Flat index of one head | 17.2 MB JSON; **2.42 MB deflated** (0.27 s); inflate and parse 0.58 s |
| Assembled into SQLite | **0.32 s**; 12.9 MB; **2.41 MB deflated**; the same bytes when built twice by the same SQLite in the same order |
| Two heads | 0.88 s; 25.8 MB |
| One path | 0.007 ms |
| One folder of 7,600 files (prefix range) | 5.4 ms |
| Paths changed between two heads | 58 ms (a Python dict: 62 ms) |
| Folders whose tree id changed | 35 ms |
| Largest 20 files | 8.5 ms |
| Serialise 25.8 MB / load it into memory (`deserialize`) | 145 ms / **15 ms** |

### The pack read in place

| Measure | Result |
|---|---|
| One zip of all 134,092 objects, as sgit writes it (stored) | 69 MB; 25.6 s to write from loose files in Python |
| Its central directory | 10.7 MB, 80 bytes a member; parsed in 0.56 s, 1.17 s with every local header |
| Read one object by offset | **5 µs** |
| Write every object loose, as a clone does today | **11.6 s** |

### One folder as ranged reads (ranges merged when less than 64 KB apart)

| Folder | Blobs | Id order (today) | Path order |
|---|---|---|---|
| `raw/c09/` | 7,600 | 2 ranges spanning 58.4 MB | 1 range, 1.12 MB |
| `raw/c09/s4/` | 1,520 | 265 ranges, 30.4 MB | 1 range, 0.22 MB |
| `raw/c09/s4/pub19/` | 76 | 70 ranges, 0.1 MB | 1 range, 0.01 MB |

### A full-text index

FTS5 over the 76,000 files (13.0 MB of text): built in **11.3 s**; 25.2 MB, 2.4 MB deflated; a query 0.2 ms.

### An unknown member in a pack, read by sgit 0.25.0

`extract_pack` wrote the object and refused only the `bare/index/` member. `sync_down` then warns and does not record the pack, so a 0.25.0 client would fetch it again on every pull.

## 3. Nine engines on the vault's graph

Milliseconds per query, warm. Every answer was checked against the plain-Python reference (`graph/b_python.py`).

| Question | Python | SQLite, int | SQLite, text | networkx | Oxigraph | DuckDB | LadybugDB | Kùzu | rdflib |
|---|---|---|---|---|---|---|---|---|---|
| Folder's children | 0.000 | 0.008 | 0.009 | 0.001 | 0.056 | 4.9 | 1.7 | 1.3 | 4.6 |
| Files under a folder (7,600) | 2.2 | 47.9 | 13.9 | 23.7 | 131.5 | 26.7 | 16.2 | 14.1 | 342.9 |
| A file's folders to the root (7) | 0.002 | 0.013 | 0.015 | 0.006 | 0.086 | 26.7 | 2.1 | 1.8 | 3.5 |
| Every ancestor of the head (19,999) | 7.8 | 22.3 | 47.6 | 18.3 | 107.3 | 228.1 | 1,971 | 2,147 | RecursionError |
| Merge base | 52.0 | 89.5 | 211.3 | 55.2 | 449.8 | 552.9 | 5,307 | 5,265 | RecursionError |
| base..head (110) | 16.9 | 79.3 | 161.2 | 34.9 | 230.8 | 611.6 | 4,843 | 5,032 | RecursionError |
| Commits that changed a file | 0.000 | 0.007 | 0.007 | 0.005 | 0.054 | 6.8 | 1.5 | 1.4 | 3.8 |
| Paths that hold a blob | 0.000 | 0.007 | 0.007 | 0.001 | 0.048 | 5.0 | 1.4 | 1.3 | 4.5 |
| Load (s) | 0.76 | 3.07 | 2.28 | 1.83 | 4.90 | 0.41 | 2.10 | 2.00 | 11.16 |
| On disk (MB) | memory | 52.2 | 118.5 | memory | 56.2 | 9.4 | 46.7 | 51.5 | memory |
| Deflated (MB) | | 15.0 | 18.5 | | | | | | |

Versions: pyoxigraph 0.5.13, duckdb 2.0.0, real_ladybug 0.15.3, kuzu 0.11.3 (archived on 10 October 2025), networkx 3.7, rdflib 7.6.0. Oxigraph's N-Triples export was 48 MB, 3.8 MB deflated.

### With generation numbers instead of a walk

| Measure | Result |
|---|---|
| Generation numbers for 20,003 commits | 14 ms |
| Merge base (git's paint-down walk, newest generation first) | **0.101 ms**, exact |
| base..head | **0.093 ms**, exact |

### A two-hop question: files changed in the same commits as the most-changed file (32)

| Engine | ms |
|---|---|
| Python dicts | 0.003 |
| SQLite, one self-join | 0.020 |
| Oxigraph, SPARQL | 0.119 |
| DuckDB, self-join | 16.0 |
| LadybugDB, Cypher | 22.3 |

### What needed a second attempt

| Engine | First form | Result | Second form | Result |
|---|---|---|---|---|
| SQLite | recursive step with the planner's join order | **182,507 ms** for the folder walk (whole benchmark stopped after 10 minutes) | `FROM sub CROSS JOIN t`, plus `ANALYZE` | 13.9 ms |
| Oxigraph | merge base as two `parent*` paths on one variable | over 10 minutes | two `SELECT DISTINCT` subqueries | 450 ms |
| Oxigraph | base..head with `FILTER NOT EXISTS` | over the limit | `MINUS` over a subquery | 231 ms |
| LadybugDB, Kùzu | `-[:PARENT* SHORTEST 1..30000]->` | binder error: 30 hops at most | `CALL var_length_extend_max_depth=30000` | as in the table |
| rdflib | `parent+` | `RecursionError` at about 1,000 commits | none | recorded as a failure |

### Encrypted triples

| Measure | Result |
|---|---|
| All triples as JSON | 39.0 MB; 3.69 MB deflated |
| Dictionary-encoded (308,151 terms, three int32 columns) | 16.4 MB; **3.02 MB deflated** |
| Encrypt the whole set (AES-GCM) / decrypt, inflate and parse | 3 ms / 351 ms |
| One member per commit | 20,003 members, median **203 bytes**, 4.0 MB; 477 ms to encrypt all |
| HMAC of every term | 786 ms |
| What the shape alone shows with hashed names | 58,062 folders, the largest holding 20; one file changed 8 times; commits per day |

### MGraph-DB through its API

1,000 nodes and edges in 0.47 s and 5,000 in 2.19 s: about **0.44 ms per node and edge**. A walk of 5,000 hops took 9.7 ms.

## 4. MGraph-DB, Memory-FS and indexes the writer pays for

### MGraph-DB 1.18.0 loaded from its own JSON

| Nodes and edges | Graph JSON | `json.loads` | Typed load | Fast-create load | Index build | Index JSON | Index save | Typed index reload | Peak memory |
|---|---|---|---|---|---|---|---|---|---|
| 10,000 | 3.8 MB | 0.05 s | 3.65 s | 1.24 s | 0.89 s | 3.2 MB | 0.34 s | 1.60 s (fast: 1.45 s) | 142 MB |
| 50,000 | 19.1 MB | 0.23 s | 18.65 s | 7.83 s | 4.47 s | 15.8 MB | 2.18 s | 10.85 s (fast: 10.63 s) | 669 MB |
| 100,000 | 38.2 MB | 0.44 s | 37.41 s | 15.45 s | 10.52 s | 31.6 MB | 6.38 s | 22.97 s (fast: 21.38 s) | 1,291 MB (fast: 1,380 MB) |

Fast-create is `Type_Safe__Config(fast_create=True, skip_validation=True)` from osbot-utils 3.75.0, documented as being for trusted data.

### Memory-FS 0.41.0: reading one member of a zip

| Zip | `Storage_FS__Zip.file__bytes` | `ZipFile` open | `ZipFile` read | Offset index built | Read by offset |
|---|---|---|---|---|---|
| 1,000 members, 0.5 MB | 6.6 ms | 3.5 ms | 21 µs | 0.4 ms | 1.8 µs |
| 10,000 members, 5.2 MB | 103.6 ms | 51 ms | 45 µs | 6.8 ms | 3.2 µs |
| 134,092 members, 69 MB (the vault packed) | **1,304 ms** | 586 ms | 51 µs | 135 ms | **5.2 µs** |

`Storage_FS__Zip` holds the zip in memory and parses its directory twice per read, once in `file__exists` and once to read.

### The writer-pays index of the vault

| Measure | Result |
|---|---|
| Full build: one JSON per folder (entries and subtree totals), blob → paths, file → commits, commits | **3.51 s**, plus 1.04 s to write the zip |
| The zip | 22.65 MB, 58,831 members: 58,062 folders (11.77 MB, median 226 bytes) and 3 × 256 cross-reference shards (about 1.1 MB each, median 4.4 to 4.6 KB) |
| One commit of 5 files, incrementally | **38 members rewritten, 57 KB, 10.4 ms**; 27 of them folders on the files' paths |
| Reader: open by parsing the central directory | 910 ms |
| List a folder | 0.19 ms, 1 member |
| Files and bytes under `raw/c09` (7,600 files, 1,296,478 bytes, from rolled-up totals) | 0.03 ms, 1 member |
| Does a file exist, and its blob | 0.07 ms, 1 member |
| Every file under `raw/c09/s4`, walked folder by folder | 36.5 ms, 1,161 members |
| Paths that hold a blob | 0.27 ms, 1 member |
| Commits that changed a file | 0.18 ms, 1 member |
| Merge base, commits sharded by hash | 56.9 ms, **97 members** |
| base..head, commits sharded by hash | 19.8 ms, 89 members |

**Second layout:** commits sharded by generation, in ranges of 1,000, with a commit → generation map, and an offset table written as the zip's first member, padded to a fixed size.

| Measure | Result |
|---|---|
| Layout and write | 1.36 s; 23.39 MB; 58,598 members; the offset table 709 KB |
| Reader open from the offset table, no central directory | **49.5 ms** |
| Merge base | 24.6 ms, **3 members** |
| base..head | 9.5 ms, 3 members |

### A Wikipedia-sized link graph

| Measure | 100,000 pages | 1,000,000 pages |
|---|---|---|
| Links | 2,489,692 | 24,972,678 |
| Shards per kind | 256 | 4,096 |
| Writer: backlinks / shards / zip | 0.6 s / 3.7 s / 0.0 s | 15.1 s / 40.4 s / 1.5 s |
| Zip | 15.6 MB, 1,025 members | 188.8 MB, 16,385 members |
| Outlinks / backlinks / titles / title index | 6.9 / 7.5 / 0.5 / 0.5 MB | 84.1 / 90.5 / 6.3 / 6.0 MB |
| Median shard (outlinks) | 26.9 KB | 20.5 KB |
| Outlinks of a page | 1.9 ms, 1 shard | 0.9 ms, 1 shard |
| Backlinks of a popular page | 1.6 ms, 1 shard (4,614 links) | 2.8 ms, 1 shard (18,494 links) |
| Title → id → outlinks | 1.2 ms, 2 shards | 0.8 ms, 2 shards |
| Pages two links away | 8.3 ms, 7 shards | 9.5 ms, 12 shards |
| **A fresh reader process: open** | 0.7 ms, 11 MB | **18 ms, 16 MB** |
| Ten shortest paths, cold: median / worst | 29.4 / 43.5 ms; 26 / 41 shards | **74.9 / 279.6 ms; 66 / 283 shards** |
| Hops in those paths | 3 to 5 | 4 to 6 |
| The reader's peak memory | 40 MB | **152 MB** |
| All links as compact arrays (int32, CSR) | 21.5 MB; loaded in 19 ms; paths in 0.1 to 0.2 ms | 215.8 MB; loaded in 700 ms; paths in 0.3 to 1.0 ms |

English Wikipedia reports about 7.25 million articles, so the million-page graph is about a seventh of it by pages. Its real link count was not checked here.

## 5. An index delta in every commit pack

1,000 commits of five random files each on the 76,000-file vault (`deltas/`, seed 5). A snapshot carries the whole index; each commit pack carries only what its commit changed.

| Measure | Whole shards in each delta | Folder files plus a change list |
|---|---|---|
| Writer, 1,000 commits | 8.04 s | **0.92 s** |
| Members per delta, median | 41 | **27** (the folders on the five paths, and the list) |
| Size per delta, median | 47.7 KB | **3.1 KB**; the change list alone 253 bytes |
| 1,000 deltas | 47.08 MB | **3.05 MB** |
| The snapshot it sits on | 8.7 MB, 58,318 members | 7.34 MB |

**The reader, with whole-shard deltas:** a map of each member's newest version across the 1,000 deltas (10,620 entries) took 6.6 ms to build. A read through it took 8.0 µs, and gave exactly the writer's final state. Merging all 1,000 deltas into a local copy took 15.5 ms.

**The reader, with change lists:** blob → paths built from the snapshot in 155 ms, and all 1,000 change lists applied to it, with file → commits, in 48.6 ms.

**Change over time, from the deltas alone:** the commits that touched `raw/c03/` (393 of 1,000) were found in 1.45 ms.

## 6. What did not work, or was not measured

- rdflib cannot walk a deep history (RecursionError).
- Kùzu is archived; its numbers are kept for reference only.
- DuckPGQ, DuckDB's SQL/PGQ extension, was not tested: extensions download at run time.
- MGraph-DB 1.18.0 does not use Memory-FS, and Memory-FS 0.41.0 has no S3 provider among its storage providers (memory, local disk, SQLite, zip).
- Cold starts, concurrent readers, slow disks and memory limits were not measured anywhere on this page.
