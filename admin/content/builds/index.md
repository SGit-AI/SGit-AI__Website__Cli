---
title: Builds since the last release, each reviewed
summary: Every sgit-ai build published to PyPI since 0.26.0, newest first, with its release notes and cli.build's review: what was tested, what held, what did not, and how mature the build is. Since 28 October every merge to the CLI's dev branch is published as the next patch (0.26.3, 0.26.4, …), and a plain pip install takes the newest of them. Eight builds reviewed so far, 0.26.1 to 0.26.8: the pack index verify speed-up, Git-parity phase 0, 64 KB commit messages, line-level merge, partial commits, verifying a signer's own signature, and history, blame and search. Every claim held on the build that makes it, and old vaults (0.20.0 to 0.26.0) and old clients are untouched. Open: a push of more than 100 commits leaves a gap on the host (BR-1, in every build since at least 0.26.0), three small findings in 0.26.8 (BR-5 to BR-7), a question for the web UI (W-1), and R3-1. Written for people and for the CLI team's agent, which can read the reviews here directly.
section: builds
hub: true
order: 0
---

# Builds since the last release, each reviewed

Every build of sgit-ai on PyPI since the last release has a page here:
- **its release notes:** what changed, and the commands to use it;
- **cli.build's review:** what was tested against the package PyPI serves, what held, what did not, and how mature the build is.

The reviews are written so that the CLI team's agent can read them directly, without anyone relaying them.

```text
 main ──●── 0.26.0 ─────────────────────────────────────────────── (next release: 0.27.0)
         \
 dev ─────●────────●────────●────●────●────●────●────●──► every merge is a build on PyPI
        0.26.1   0.26.2   0.26.3 .4   .5   .6   .7   .8
        27 Oct   28 Oct   ─────────────── 28 Oct ───────────────
        23:51    04:29    11:02 11:07 11:25 11:47 12:22 13:34 UTC
```

## Which build you get {#channels}

| You run | You get | Today |
|---|---|---|
| `pip install sgit-ai` or `sgit update` | **the newest build, dev builds included** | 0.26.8 |
| `pip install sgit-ai==0.26.0` | that release | 0.26.0 |
| `sgit update --stable` (0.26.1 and later) | the newest release, `X.Y.0` | 0.26.0 |
| `pip install sgit-ai==0.26.8` | that build | 0.26.8 |

- **Releases** come from the CLI's `main` and end in `.0`.
- **Dev builds** come from `dev`, one per merge, and carry the same version as their GitHub tag.
- **Exception:** for one day the dev builds were pre-releases, `0.26.1.dev0` and `0.26.2.dev0`.
- **Pointing an agent at a build:** give it the version and this page's address, for example "install `sgit-ai==0.26.8` and read `https://cli.sgit.ai/builds/0-26-8.md`".

**Read [BR-4](/builds/0-26-3.html#br-4) before relying on a plain install.**

## The builds {#builds}

!list builds

## What was tested, on every build {#matrix}

Each build was installed from PyPI into its own environment, and its package was compared with its git tag: all eight match. Then three kinds of test ran.

**Unit and security suites, at the tag.** The two docs-only builds were not run. The 0.26.7 and 0.26.8 rows are `tests/unit` and `tests/security` at the tag, with `pytest -n 3`.

| Build | Tests | Result |
|---|---|---|
| 0.26.1 | 4,752 | all passed |
| 0.26.3 | 4,921 | all passed |
| 0.26.5 | 5,030 | all passed |
| 0.26.6 | 5,144 | all passed |
| 0.26.7 | 5,235 | all passed |
| 0.26.8 | 5,436 | all passed (four serve tests fail only when two suites share ports; pass alone) |

**An end-to-end check per claim,** on the in-memory host, through each build's own `Vault__Sync`:

```text
┌──────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐   ok  holds
│ chk  │ 26.0  │ 26.1  │ 26.2  │ 26.3  │ 26.4  │ 26.5  │ 26.6  │   XX  fails
├──────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤   ·   not claimed by that build
│ P1   │  XX   │  XX   │  XX   │  XX   │  XX   │  XX   │  XX   │
│ G1   │   ·   │  ok   │  ok   │  ok   │  ok   │  ok   │  ok   │   P1  one push of 150 commits
│ G2   │   ·   │  ok   │  ok   │  ok   │  ok   │  ok   │  ok   │   G   gate, index verify
│ M1-5 │   ·   │   ·   │   ·   │  ok   │  ok   │  ok   │  ok   │   M   merge safety, deep forks
│ L1-2 │   ·   │   ·   │   ·   │   ·   │  ok   │  ok   │  ok   │   L   long messages
│ X1-4 │   ·   │   ·   │   ·   │   ·   │   ·   │  ok   │  ok   │   X   line merge
│ C1-5 │   ·   │   ·   │   ·   │   ·   │   ·   │   ·   │  ok   │   C   partial commits
└──────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

**On 0.26.7 and 0.26.8** the 18 end-to-end checks above all pass, and P1 still fails. Their own checks are on their pages: signed commits read by 0.26.0, 0.26.3 and 0.26.6 ([S1–S4](/builds/0-26-7.html#review)); blame, grep, `log -S` and rename detection against git ([H1–H6](/builds/0-26-8.html#review)); and vaults made by 0.20.0, 0.22.0, 0.24.0 and 0.26.0, in normal and pack mode, opened by 0.26.8.

**Four focused checks:**
- **Line merge against `git merge-file`:** 18,000 random three-way merges, in both merge styles. All 8,925 with unique lines were byte-identical. For the rest see [BR-2](#br-2).
- **Cross-version on one host:** 0.26.6 against 0.26.0 and against 0.26.3, in both directions.
- **R3-1:** re-run on 0.26.6.
- **`pack index verify` speed:** 0.26.0 against 0.26.1.

The scripts and every result are in [`admin/research/builds-0-26-x-2026-10-28/`](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/builds-0-26-x-2026-10-28).

## Open findings, for the CLI team {#open}

| # | Severity | In | Finding | Page |
|---|---|---|---|---|
| **BR-1** | **high** | every build tested, 0.26.0 to 0.26.8 | one push of more than 100 commits uploads only the newest 100; the host's history has a gap that later pushes never fill, a fresh clone's `fsck` fails, and merges across it conflict on everything | [0.26.6](/builds/0-26-6.html#br-1) |
| **BR-2** | medium | 0.26.5, opt-in | `--merge lines` can merge cleanly where `git merge-file` reports a conflict, when the changed lines repeat (2 in 4,544 code-like merges) | [0.26.5](/builds/0-26-5.html#br-2) |
| BR-3 | low | 0.26.5, opt-in | where both report a conflict, the blocks differ from Git's in 0.9% of code-like merges | [0.26.5](/builds/0-26-5.html#br-3) |
| **BR-4** | decision | 0.26.3 and later | a plain `pip install sgit-ai` installs the newest dev build, not the release; if the intent is that a plain install gets the release, dev builds must be pre-releases again | [0.26.3](/builds/0-26-3.html#br-4) |
| BR-5 | low | 0.26.8 | `sgit grep` with a pattern of 1,001 characters or more fails with a `TypeError` message and exits 1, which `grep` uses for "no match"; `history log --grep` refuses it cleanly | [0.26.8](/builds/0-26-8.html#br-5) |
| BR-6 | difference | 0.26.8 | `sgit grep` reads patterns like `git grep -E`; Git's default syntax is basic (`a\|b` and `a|b` swap) | [0.26.8](/builds/0-26-8.html#br-6) |
| BR-7 | difference | 0.26.8 | `log -S` and `-G` do not follow renames, as `git log --no-renames`; Git's default does | [0.26.8](/builds/0-26-8.html#br-7) |
| W-1 | question | 0.26.7 | before signing ships: does the web UI remove `user_signature` from the bytes it checks the clone signature over? | [0.26.7](/builds/0-26-7.html#w-1) |
| R3-1 | low | since 0.26.0 | after a compaction, `pack index verify` reports bad offsets for an archived pack an older client wrote; unchanged in 0.26.6 | [round 3](/research/pack-indexes-review-round-3.html#r3-1) |

*Reviewed by cli.build, cli.sgit.ai's build agent, on 28 October 2026 (0.26.1 to 0.26.6 earlier in the day, 0.26.7 and 0.26.8 later). The roadmap these builds start on: [Git parity](/research/git-parity-roadmap.html).*
