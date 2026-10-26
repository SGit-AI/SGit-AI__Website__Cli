# Indexes, graph engines and xref shards: the proofs of concept of 26 October 2026

Every script and every raw result behind three articles on cli.sgit.ai, kept so the numbers can be checked and re-run:

- [Indexes in the pack](https://cli.sgit.ai/articles/indexes-in-the-pack.html) (`indexes/`)
- [A vault is already a graph](https://cli.sgit.ai/articles/a-vault-is-already-a-graph.html) (`graph/`)
- [Indexes the writer pays for](https://cli.sgit.ai/articles/indexes-the-writer-pays-for.html) (`mgraph/`, `wiki/`)

The record of every number, in one page: [Graph and index measurements, 26 October 2026](https://cli.sgit.ai/research/graph-and-index-measurements-2026-10-26.html).

Written and run by cli.build, cli.sgit.ai's build agent, on a 4-core cloud sandbox with 15 GB of memory and a fast local disk:
Python 3.13.16, SQLite 3.45.1, sgit-ai 0.25.0. Nothing here is sgit code; these are prototypes against copies of the data.

## Layout

| Folder | What it holds |
|---|---|
| `vault/genbig.py` | writes the 76,000 files of the benchmark vault (10 countries, 5 sectors, 20 publishers, 19 pages, 2 captures, a `meta.json` and a `text.md` each) |
| `indexes/` | the flat index of a head, SQLite assembled from it, a pack read in place, path-ordered ranges, a full-text index |
| `graph/` | the 482,532-triple dataset and the eight questions in nine engines, each checked against `b_python.py` |
| `mgraph/` | MGraph-DB loaded from its own JSON; Memory-FS's zip reads; the writer-pays xref index of the vault, two layouts |
| `wiki/` | a synthetic Wikipedia-sized link graph: sharded outlinks, backlinks and titles, read on demand, against compact arrays |
| `deltas/` | 1,000 commits of five files, each pack carrying only its index changes: whole shards (`deltas.py`) against folder files plus a change list (`deltas_lean.py`) |
| `results/` | every result file the scripts wrote, and `console-output.md` for the runs that only printed |

## Re-running

The scripts take a working folder in the environment variable `S`. They expect:

- `$S/bench/v`: an sgit clone holding the files from `vault/genbig.py`, committed with sgit-ai 0.25.0 and then committed again
  after one edit, so its `.sg_vault/local/flat-cache/` holds two heads. The scripts name the two flat-cache files of the run
  recorded here (`obj-cas-imm-7473af178535.json`, the head, and `obj-cas-imm-2f25b8d1c74e.json`); a new run has new tree
  ids, so put yours in their place.
- the scripts of each folder copied to `$S/idxexp`, `$S/gx`, `$S/mg` and `$S/wk`, the folders they write to.

The engines were installed from PyPI into a separate environment, never into sgit's: `pyoxigraph 0.5.13`, `duckdb 2.0.0`,
`real_ladybug 0.15.3` (LadybugDB), `kuzu 0.11.3` (archived), `networkx 3.7`, `rdflib 7.6.0`, `mgraph-db 1.18.0`,
`memory-fs 0.41.0`, `osbot-utils 3.75.0`, and `cryptography` for `graph/b_crypt.py`.

Order: `graph/gen.py`, then `graph/b_python.py` (it writes `truth.json`, the reference every other engine is checked
against), then any of the others. `mgraph/xref_index.py` comes before `mgraph/xref_v2.py`. `wiki/wiki.py` takes the number
of pages and of shards: `python3 wiki.py 1000000 4096`.

## Things to know before trusting a number

- Timings are warm, single process, on one machine. Cold starts, concurrency and memory limits were not measured.
- The history in `graph/` and the link graph in `wiki/` are synthetic, generated with fixed seeds.
- The merge base is computed as the newest common ancestor by time in every engine; on this history it is the true one.
- Each engine got one rewrite where its first query form was unreasonably slow; `results/console-output.md` lists them.
