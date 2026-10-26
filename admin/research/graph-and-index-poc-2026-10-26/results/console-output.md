# Console output of the runs whose results were printed, not written to a file

Recorded on 26 October 2026 by cli.build, copied from the runs as they printed. The machine was a 4-core cloud sandbox with
15 GB of memory and a fast local disk; Python 3.13.16 and SQLite 3.45.1. The JSON files beside this one hold the runs that
wrote their own results.

## indexes/exp_sqlite.py: the flat index of one head, and SQLite assembled from it

```
flat member: 76000 files, 58062 folders; json 17.2 MB, deflated 2.42 MB (0.27 s)
inflate+parse: 0.58 s
sqlite assembly, one head: 0.32 s; file 12.9 MB, deflated 2.41 MB
same bytes twice (same sqlite, same order): True
two heads: 0.88 s, 25.8 MB
queries:
  one path: 0.007 ms, 1 rows
  one folder (raw/c09/), prefix range: 5.411 ms, 7600 rows
  diff two heads (changed or added): 57.797 ms, 1 rows
  folders whose tree differs: 34.799 ms, 7 rows
  largest 20 files: 8.497 ms, 20 rows
serialize 25.8 MB in 145 ms; deserialize into memory 15 ms
python dict diff for comparison: 62 ms, 1 rows
```

## indexes/exp_pack.py: one pack of every object, read in place, and scoped ranges

```
pack of 134092 objects by id: 25.6 s, 69 MB
pack index from the central directory (with local headers): 1.17 s for 134092 members
  central directory alone: 0.56 s
read in place: 5 us per object (warm page cache)
extract every object loose (today): 11.6 s
scope raw/c09/: 7600 blobs; ranges by id 2 (58.4 MB), by path 1 (1.12 MB)
scope raw/c09/s4/: 1520 blobs; ranges by id 265 (30.4 MB), by path 1 (0.22 MB)
scope raw/c09/s4/pub19/: 76 blobs; ranges by id 70 (0.1 MB), by path 1 (0.01 MB)
```

## indexes/exp_fts.py: the zip directory, and a full-text index

```
central directory: 10.7 MB of a 69 MB pack (80 bytes a member)
fts5: True
full-text index over 76000 files (13.0 MB of text): built in 11.3 s; 25.2 MB, deflated 2.4 MB; a query 0.2 ms (50 hits)
```

## The 0.25.0 client and an unknown pack member

sgit-ai 0.25.0 from PyPI, `Vault__Packs.extract_pack` on a pack holding one object and one `bare/index/flat/...` member:

```
{'extracted': 1, 'refused': ['bare/index/flat/obj-cas-imm-7473af178535'], 'objects': ['obj-cas-imm-00004b0b685f']}
```

`sync_down` then warns and does not record the pack as absorbed, so it would be fetched again on every pull.

## graph/gen.py: the dataset

```
482532 triples {'tree': 58062, 'contains': 134061, 'blob': 76000, 'size': 76000, 'ts': 20003, 'changed': 98005, 'parent': 20401} commits 20003
```

## SQLite's query plan for the recursive folder walk (graph/b_sqlite.py, text triples)

```
default plan:   SEARCH t USING COVERING INDEX pos (p=?)  then SCAN sub   ->  13405 rows in 182507.2 ms
CROSS JOIN:     SCAN sub  then SEARCH t USING COVERING INDEX spo (p=? AND s=?)  ->  13405 rows in 13.9 ms
```

The first run of the whole SQLite benchmark, before the join order was forced, was stopped after more than ten minutes.

## Engines that needed a second form of a query

- **Oxigraph:** the merge base written as two `parent*` paths joined on one variable ran past ten minutes; written as two
  `SELECT DISTINCT` subqueries it took 450 ms. base..head with `FILTER NOT EXISTS` also ran past the limit; with `MINUS`
  over a subquery, 231 ms.
- **LadybugDB and Kùzu:** variable-length paths are capped at 30 hops by default (`Binder exception: Upper bound of rel
  exceeds maximum: 30`); `CALL var_length_extend_max_depth=30000` lifts it.
- **rdflib:** `parent+` over the history raised `RecursionError: maximum recursion depth exceeded` (979 nested calls in
  `rdflib/paths.py _fwd`); there is no second form, so it is recorded as a failure.

## graph/b_gen.py: generation numbers

```
generation numbers for 20003 commits: 14 ms
  merge_base     0.101 ms  cd6a57bbae76f  ok
  base_to_head   0.093 ms  110  ok
```

## graph/b_crypt.py: shipping the triples encrypted (AES-GCM, `cryptography` as sgit uses it)

```
triples as JSON: 39.0 MB, deflated 3.69 MB
dictionary-encoded: 16.4 MB, deflated 3.02 MB (308151 distinct terms)
one member: encrypt 3 ms; decrypt + inflate + parse 351 ms
per-commit shards: 20003 members, median 203 bytes, total 4.0 MB, encrypt all 477 ms
HMAC of 308151 terms: 786 ms
what the shape alone tells a host: 58062 folders; the largest has 20 children; files changed most often: 8 times; commits per day are visible from the ts edges
```

## graph/b_mgraph.py: MGraph-DB through its API

```
MGraph-DB: 1000 nodes + 1000 edges in 0.47 s (467 us per node+edge)
MGraph-DB: 5000 nodes + 5000 edges in 2.19 s (437 us per node+edge)
walk of 5000 hops: 9.7 ms
```

## mgraph/mg_scale.py: MGraph-DB loaded from its own JSON

Default Type_Safe:

```
{"nodes": 10000, "edges": 9999, "graph_json_mb": 3.8, "json_loads_s": 0.05, "typed_load_s": 3.65, "index_build_s": 0.89, "index_json_mb": 3.2, "index_save_s": 0.34, "index_typed_reload_s": 1.6, "walk_hops": 21, "walk_ms": 0.2, "max_rss_mb": 142}
{"nodes": 50000, "edges": 49999, "graph_json_mb": 19.1, "json_loads_s": 0.23, "typed_load_s": 18.65, "index_build_s": 4.47, "index_json_mb": 15.8, "index_save_s": 2.18, "index_typed_reload_s": 10.85, "walk_hops": 24, "walk_ms": 3.1, "max_rss_mb": 669}
```

With `Type_Safe__Config(fast_create=True, skip_validation=True)` (`FAST=1`):

```
{"fast": true, "nodes": 10000, "edges": 9999, "graph_json_mb": 3.8, "json_loads_s": 0.03, "typed_load_s": 1.24, "index_build_s": 0.89, "index_json_mb": 3.2, "index_save_s": 0.36, "index_typed_reload_s": 1.45, "walk_hops": 21, "walk_ms": 0.3, "max_rss_mb": 151}
{"fast": true, "nodes": 50000, "edges": 49999, "graph_json_mb": 19.1, "json_loads_s": 0.2, "typed_load_s": 7.83, "index_build_s": 4.6, "index_json_mb": 15.8, "index_save_s": 2.83, "index_typed_reload_s": 10.63, "walk_hops": 24, "walk_ms": 3.6, "max_rss_mb": 714}
```

At 100,000 nodes (`results/mg_100k_default.jsonl` and `results/mg_100k_fast.jsonl`):

```
{"fast": false, "nodes": 100000, "edges": 99999, "graph_json_mb": 38.2, "json_loads_s": 0.44, "typed_load_s": 37.41, "index_build_s": 10.52, "index_json_mb": 31.6, "index_save_s": 6.38, "index_typed_reload_s": 22.97, "walk_hops": 26, "walk_ms": 0.3, "max_rss_mb": 1291}
{"fast": true, "nodes": 100000, "edges": 99999, "graph_json_mb": 38.2, "json_loads_s": 0.62, "typed_load_s": 15.45, "index_build_s": 10.25, "index_json_mb": 31.6, "index_save_s": 5.16, "index_typed_reload_s": 21.38, "walk_hops": 26, "walk_ms": 0.2, "max_rss_mb": 1380}
```
