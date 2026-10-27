# The pack-indexes reviews of 26 and 27 October 2026: scripts and results

The scripts behind cli.build's three reviews of the pack-indexes implementation in SGit-AI__CLI, and the release article:

- [Round 1](https://cli.sgit.ai/research/pack-indexes-review-round-1.html), at `a9f24d86`
- [Round 2](https://cli.sgit.ai/research/pack-indexes-review-round-2.html), at `58f52a42`
- [Round 3](https://cli.sgit.ai/research/pack-indexes-review-round-3.html), at the dev merge `09172b0f`
- [The release article](https://cli.sgit.ai/articles/pack-indexes-shipped.html)

Each script runs against an SGit-AI__CLI checkout given as its first argument and uses that checkout's own test helpers
(`tests/_helpers/pack_env.py`, the in-memory host). Nothing here talks to a real server.

| Script | What it checks |
|---|---|
| `scripts/fuzz_index.py <cli> <seed> <rounds>` | index answers against the tree walk: two writers, three-way merges, compaction, folder deletes, deep adds, renames; a reader clone pulling through the indexes |
| `scripts/selective.py`, `scripts/selective2.py` | `sgit checkout` over an uncommitted edit (B2); a lost `checkout.json` on a pack clone (M2) |
| `scripts/store_race.py` | the pack store under 8 threads with more packs than its handle limit (M1) |
| `scripts/push_cost.py <vault>`, `scripts/path_order_fix.py <vault>` | the per-push cost of ordering a pack (B1), and the pruned version |
| `scripts/m6.py` | `history log` coverage from indexes after compaction (M6) |
| `scripts/bench.py` | end to end on the 76,000-file vault: commit, push, clones, scoped clone, pulls, history log, compaction |
| `scripts/prof.py` | the profile that found the clone's tree walk (M5) |
| `scripts/step.py`, `scripts/narrow.py`, `scripts/dbg.py` | the cross-version check with sgit-ai 0.25.0: each step in its own Python, one in-memory host saved between steps; and the narrowing of R3-1 |

`results/bench_<commit>.json` holds the end-to-end timings for each commit benchmarked. The vault is the 76,000 files of
`../graph-and-index-poc-2026-10-26/vault/genbig.py`; the machine a 4-core cloud sandbox, one process, warm.
