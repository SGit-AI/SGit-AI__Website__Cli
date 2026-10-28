---
title: Builds since the last release, each reviewed
summary: Every sgit-ai build published to PyPI since 0.26.0, newest first, with its release notes and cli.build's review: what was tested, what held, what did not, and how mature the build is. Since 28 October every merge to the CLI's dev branch is published as the next patch (0.26.3, 0.26.4, …), and a plain pip install takes the newest of them. Twelve builds reviewed so far, 0.26.1 to 0.26.12.dev0: the pack index verify speed-up, Git-parity phase 0, 64 KB commit messages, line-level merge, partial commits, verifying a signer's own signature, history, blame and search, the BR-1 push fix, signing with your own key, a differ that is Git's, and the return to pre-release dev builds. Every claim held on the build that makes it, and old vaults (0.20.0 to 0.26.0) and old clients are untouched. Closed: BR-1 (0.26.9), BR-2 and BR-3 (0.26.10), BR-4 (0.26.12.dev0, once the yank is done). Open: four small findings (BR-5 to BR-8), a question for the web UI (W-1), and R3-1. Written for people and for the CLI team's agent, which can read the reviews here directly.
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
 dev ─────●────────●────────●────●────●────●────●────●────●────●────●────●──► every merge is a build on PyPI
        0.26.1   0.26.2   0.26.3 .4   .5   .6   .7   .8   .9   .10  .11  .12.dev0
        27 Oct   28 Oct   ─────────────────────── 28 Oct ───────────────────────────
        23:51    04:29    11:02 11:07 11:25 11:47 12:22 13:35 16:14 16:30 16:41 19:09 UTC
```

## Which build you get {#channels}

| You run | You get | Today |
|---|---|---|
| `pip install sgit-ai` | the newest release. **Until the yank of 0.26.3 to 0.26.11 is done, the newest plain build** | 0.26.11 now, 0.26.0 after the yank |
| `pip install --pre sgit-ai` or `sgit update` on a dev install | the newest dev build (pre-release, from 0.26.12.dev0) | 0.26.12.dev0 |
| `pip install sgit-ai==0.26.0` | that release | 0.26.0 |
| `sgit update --stable` (0.26.1 and later) | the newest release, `X.Y.0` | 0.26.0 |
| `pip install sgit-ai==0.26.11` | that build (a yanked version stays installable by its number) | 0.26.11 |

- **Releases** come from the CLI's `main` and end in `.0`.
- **Dev builds** come from `dev`, one per merge, and carry the same version as their GitHub tag.
- **Exception:** for one day the dev builds were pre-releases, `0.26.1.dev0` and `0.26.2.dev0`.
- **Pointing an agent at a build:** give it the version and this page's address, for example "install `sgit-ai==0.26.11` and read `https://cli.sgit.ai/builds/0-26-11.md`".

**[BR-4](/builds/0-26-3.html#br-4): resolved by [0.26.12.dev0](/builds/0-26-12.html) once the CLI team yanks 0.26.3 to 0.26.11; until then a plain install still takes 0.26.11.**

## The builds {#builds}

!list builds

## What was tested, on every build {#matrix}

Each build was installed from PyPI into its own environment, and its package was compared with its git tag: all twelve match. Then three kinds of test ran.

**Unit and security suites, at the tag.** The two docs-only builds were not run. The 0.26.7 and 0.26.8 rows are `tests/unit` and `tests/security` at the tag, with `pytest -n 3`.

| Build | Tests | Result |
|---|---|---|
| 0.26.1 | 4,752 | all passed |
| 0.26.3 | 4,921 | all passed |
| 0.26.5 | 5,030 | all passed |
| 0.26.6 | 5,144 | all passed |
| 0.26.7 | 5,235 | all passed |
| 0.26.8 | 5,436 | all passed (four serve tests fail only when two suites share ports; pass alone) |
| 0.26.11 | 5,623 | all passed |

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

**On 0.26.9 to 0.26.11** the 19 end-to-end checks pass, P1 included (BR-1 fixed); 4,500 line merges are byte-identical to `git merge-file` (BR-2 and BR-3 fixed); signed commits are read by clients from 0.20.0 to 0.26.11 ([0.26.10](/builds/0-26-10.html#review)); a gap made by 0.26.8 is repaired by `check upload-history`, loose and pack.

**Four focused checks:**
- **Line merge against `git merge-file`:** 18,000 random three-way merges, in both merge styles. All 8,925 with unique lines were byte-identical. For the rest see [BR-2](#br-2).
- **Cross-version on one host:** 0.26.6 against 0.26.0 and against 0.26.3, in both directions.
- **R3-1:** re-run on 0.26.6.
- **`pack index verify` speed:** 0.26.0 against 0.26.1.

The scripts and every result are in [`admin/research/builds-0-26-x-2026-10-28/`](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/builds-0-26-x-2026-10-28).

## Open findings, for the CLI team {#open}

| # | Severity | In | Finding | Page |
|---|---|---|---|---|
| ~~BR-1~~ | closed | 0.26.0 to 0.26.8 | one push of more than 100 commits uploaded only the newest 100 and left a gap on the host. **Fixed in [0.26.9](/builds/0-26-9.html)**: repro passes at 101 to 151 commits, loose and pack; `check upload-history` repairs an old gap from the clone that holds the commits | [0.26.9](/builds/0-26-9.html) |
| ~~BR-2~~ | closed | 0.26.5 to 0.26.9 | `--merge lines` merged cleanly where `git merge-file` conflicts on repeated lines. **Fixed in [0.26.10](/builds/0-26-10.html)**: the differ is a port of Git's; 4,500 merges byte-identical | [0.26.10](/builds/0-26-10.html) |
| ~~BR-3~~ | closed | 0.26.5 to 0.26.9 | conflict blocks drew differently from Git's. Fixed in 0.26.10 with BR-2 | [0.26.10](/builds/0-26-10.html) |
| ~~BR-4~~ | resolved, pending the yank | 0.26.3 to 0.26.11 | a plain `pip install sgit-ai` took the newest dev build. From [0.26.12.dev0](/builds/0-26-12.html) dev builds are pre-releases; **0.26.3 to 0.26.11 are not yanked yet**, so a plain install still gets 0.26.11 | [0.26.12](/builds/0-26-12.html) |
| BR-5 | low | 0.26.8 | `sgit grep` with a pattern of 1,001 characters or more fails with a `TypeError` message and exits 1, which `grep` uses for "no match"; `history log --grep` refuses it cleanly | [0.26.8](/builds/0-26-8.html#br-5) |
| BR-6 | difference | 0.26.8 | `sgit grep` reads patterns like `git grep -E`; Git's default syntax is basic (`a\|b` and `a|b` swap) | [0.26.8](/builds/0-26-8.html#br-6) |
| BR-7 | difference | 0.26.8 | `log -S` and `-G` do not follow renames, as `git log --no-renames`; Git's default does | [0.26.8](/builds/0-26-8.html#br-7) |
| BR-8 | low | 0.26.10 | a failed `commit -S` says "nothing was written" but leaves a blob and a tree (no commit, no ref move); a doubled `gpg:` prefix | [0.26.10](/builds/0-26-10.html#br-8) |
| W-1 | question, answered by the CLI team, not tested | 0.26.7 | signing shipped in 0.26.10 on the CLI team's statement that the web UI never verifies commit signatures and ignores unknown members; one test with a signed vault is still worth running | [0.26.7](/builds/0-26-7.html#w-1) |
| R3-1 | low | since 0.26.0 | after a compaction, `pack index verify` reports bad offsets for an archived pack an older client wrote; unchanged in 0.26.6 | [round 3](/research/pack-indexes-review-round-3.html#r3-1) |

*Reviewed by cli.build, cli.sgit.ai's build agent, on 28 October 2026 (0.26.1 to 0.26.6 earlier in the day, 0.26.7 and 0.26.8 later, 0.26.9 to 0.26.12.dev0 in the evening). The roadmap these builds start on: [Git parity](/research/git-parity-roadmap.html).*
