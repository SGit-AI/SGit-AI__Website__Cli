# Reviews of the sgit-ai builds after 0.26.0 (28 October 2026): scripts and results

The checks behind [cli.sgit.ai/builds/](https://cli.sgit.ai/builds/index.html): one page per build, 0.26.1.dev0 to
0.26.6, each with its release notes and cli.build's review. Every script runs with the Python of an installed
`sgit-ai` (`pip install sgit-ai==X.Y.Z` into its own venv) and that build's in-memory host; nothing talks to a server.
Run them with `python -I`, from a folder that is not a checkout of the CLI.

| Script | What it checks |
|---|---|
| `scripts/check_build.py [OUT.json]` | one check per claim, gated by version: P1 push gap, G1–G2 gate and `pack index verify`, M1–M5 merge safety and deep forks, L1–L2 long messages, X1–X4 line merge, C1–C5 partial commits (C1 and C2 against git) |
| `scripts/fuzz_line_merge.py <seed> <cases> [merge\|diff3]` | `Vault__Line_Merge` against `git merge-file -p` on random merges: unique lines, code-like lines, a three-letter alphabet; CRLF and missing final newlines |
| `scripts/push_gap.py N…` (`PACKS=1` for a pack vault) | BR-1: one push of N commits, one more push, then a fresh clone walks the history and runs `fsck` |
| `scripts/deep_fork.py N…` (`BATCH=50`) | a fork N commits deep on each side, disjoint files: does `pull` merge cleanly |
| `scripts/xstep.py STEP W` | cross-version on one host saved between steps: new-create, old-follow, new-follow, new-long, old-after-long |
| `scripts/verify_speed.py FILES PUSHES` | `pack index verify` timed on a pack vault |

`results/` holds `check_<version>.json` for 0.26.0 and the six builds, `lm_<seed>_<style>.json` with up to three
samples per verdict, and `suite-<tag>.txt`, the unit and security suite results at each tag (`pytest -n 4`, then
the `no_parallel` tests).
