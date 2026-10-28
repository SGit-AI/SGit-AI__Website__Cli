# Builds since the last release, each reviewed, cli.sgit.ai

> Every sgit-ai build published to PyPI since 0.26.0, newest first, with its release notes and cli.build's review: what was tested, what held, what did not, and how mature the build is. Since 28 October every merge to the CLI's dev branch is published as the next patch (0.26.3, 0.26.4, …), and a plain pip install takes the newest of them. Six builds reviewed so far, 0.26.1 to 0.26.6: the pack index verify speed-up, Git-parity phase 0, 64 KB commit messages, line-level merge and partial commits. Every claim held on the build that makes it. Open: a push of more than 100 commits leaves a gap on the host (BR-1, in every build since at least 0.26.0), and R3-1. Written for people and for the CLI team's agent, which can read the reviews here directly.

*Source: <https://cli.sgit.ai/builds/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Builds since the last release, each reviewed

Every build of sgit-ai on PyPI since the last release has a page here:
- **its release notes:** what changed, and the commands to use it;
- **cli.build's review:** what was tested against the package PyPI serves, what held, what did not, and how mature the build is.

The reviews are written so that the CLI team's agent can read them directly, without anyone relaying them.

```text
 main ──●── 0.26.0 ─────────────────────────────────────────────── (next release: 0.27.0)
         \
 dev ─────●────────●────────●────●────●────●──► every merge is a build on PyPI
        0.26.1   0.26.2   0.26.3 .4   .5   .6
        27 Oct   28 Oct   ─────── 28 Oct ───────
        23:51    04:29    11:02 11:07 11:25 11:47 UTC
```

## Which build you get {#channels}

| You run | You get | Today |
|---|---|---|
| `pip install sgit-ai` or `sgit update` | **the newest build, dev builds included** | 0.26.6 |
| `pip install sgit-ai==0.26.0` | that release | 0.26.0 |
| `sgit update --stable` (0.26.1 and later) | the newest release, `X.Y.0` | 0.26.0 |
| `pip install sgit-ai==0.26.6` | that build | 0.26.6 |

- **Releases** come from the CLI's `main` and end in `.0`.
- **Dev builds** come from `dev`, one per merge, and carry the same version as their GitHub tag.
- **Exception:** for one day the dev builds were pre-releases, `0.26.1.dev0` and `0.26.2.dev0`.
- **Pointing an agent at a build:** give it the version and this page's address, for example "install `sgit-ai==0.26.6` and read `https://cli.sgit.ai/builds/0-26-6.md`".

**Read [BR-4](../builds/0-26-3.md#br-4) before relying on a plain install.**

## The builds {#builds}

- [sgit-ai 0.26.6: commit some paths, commit some hunks, push with uncommitted changes](../builds/0-26-6.md): Dev build of 28 October 2026, from the CLI's dev at 036e33b5, and what a plain pip install gives today. sgit commit takes paths, as git commit -- paths does, and leaves every other change on disk. sgit commit -p picks hunks interactively; agents use --list-hunks and --hunk ID, with ids that refuse to pick a different hunk once the file has changed. sgit push no longer refuses uncommitted changes. One behaviour change for scripts: with -m, extra words are now paths. Reviewed by cli.build. 5,144 unit and security tests pass. commit with paths matched Git in 40 random cases, and hunk commits matched git apply --cached in 60. Maturity good. One high finding, in every build since at least 0.26.0: a push of more than 100 commits leaves a gap in the host's history (BR-1).
- [sgit-ai 0.26.5: line-level merge, opt-in](../builds/0-26-5.md): Dev build of 28 October 2026, from the CLI's dev at 43e1889c. sgit pull --merge lines and sgit branch merge --merge lines merge a file both sides changed line by line, as Git does, with Git's conflict markers in the file and --conflict diff3 for the base too. The default does not change: whole-file .conflict copies. Reviewed by cli.build. 5,030 tests pass and the four end-to-end checks hold. In 18,000 random merges against git merge-file, all 8,925 with unique lines were byte-identical. Where lines repeat, 2 of 4,544 code-like merges came out clean where Git reports a conflict (BR-2), and 0.9% placed conflict blocks differently (BR-3). Maturity good for an opt-in feature: review line-merged files before pushing.
- [sgit-ai 0.26.4: commit messages up to 64 KB](../builds/0-26-4.md): Dev build of 28 October 2026, from the CLI's dev at c495b40e. A commit message longer than 740 bytes used to fail with a raw ValueError, after the commit's blobs and trees were written; Git has no limit. The default limit stays 740 bytes, now refused before anything is written. A vault with the long-messages feature takes up to 64 KiB, and every client reads messages up to 1 MiB, the web UI's. Turning the feature on raises the vault's gate to 0.26.4, so an older sgit is told to update. Reviewed by cli.build. All checks held, including the refusal of 0.26.0 and 0.26.3 clients with a clear message. Maturity good. Wait for the 0.27.0 release before turning long-messages on in a vault that agents on 0.26.0 still use.
- [sgit-ai 0.26.3: Git-parity phase 0, merges made safe, and dev builds on PyPI](../builds/0-26-3.md): Dev build of 28 October 2026, from the CLI's dev at 16c46e89, and the first published as a plain version. It fixes the bugs the seven Git-parity designs found. sgit commit during an unresolved merge put the .conflict files into the vault; it now refuses. status shows a merge in progress. Identical content on both sides is no longer a conflict. Merges and pushes on forks deeper than 200 commits work. A nested vault is never committed. Object files are written atomically. Merges, writes and sparse commits rebuild only the changed folders. From this build, every dev merge is published as X.Y.N, and a plain pip install takes the newest. Reviewed by cli.build. 4,921 tests pass and every fix held, including a 250-commit fork that 0.26.1 merged against an empty base. Maturity good. One decision for Dinis Cruz: plain installs now get dev builds (BR-4).
- [sgit-ai 0.26.2.dev0: the Git-parity roadmap and seven designs, no code change](../builds/0-26-2.md): Pre-release of 28 October 2026, from the CLI's dev at 926c076d. The code is 0.26.1's; only the version differs. It carries the CLI team's Git-parity roadmap, sgit at parity with Git the client and then more on top, and seven designs: line merge and cherry-pick, signing with your own key, partial commits and hooks, renames, blame and grep, bisect, worktree, and rebase. All are published here as research. Reviewed by cli.build: the package matches its tag, and the 0.26.1 checks hold.
- [sgit-ai 0.26.1.dev0: pack index verify 120 times faster, and a new pack vault's gate fixed](../builds/0-26-1.md): Pre-release of 27 October 2026, from the CLI's dev at b9c8baac. sgit pack index verify took about 40 minutes on the newsroom's vault and printed nothing. It is now about 300 times faster, prints a line per pack, and --last N checks only the newest packs. A new pack vault is gated at what its features need, 0.24.0, not at the creating build's version, which fixes R3-2. sgit update gains --stable. Reviewed by cli.build. 4,752 tests pass. On 8,000 files and 6 packs, verify went from 82.9 s on 0.26.0 to 0.69 s. A new pack vault reads min_client 0.24.0. Maturity good. R3-1 is still open.

## What was tested, on every build {#matrix}

Each build was installed from PyPI into its own environment, and its package was compared with its git tag: all six match. Then three kinds of test ran.

**Unit and security suites, at the tag.** The two docs-only builds were not run.

| Build | Tests | Result |
|---|---|---|
| 0.26.1 | 4,752 | all passed |
| 0.26.3 | 4,921 | all passed |
| 0.26.5 | 5,030 | all passed |
| 0.26.6 | 5,144 | all passed |

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

**Four focused checks:**
- **Line merge against `git merge-file`:** 18,000 random three-way merges, in both merge styles. All 8,925 with unique lines were byte-identical. For the rest see [BR-2](#br-2).
- **Cross-version on one host:** 0.26.6 against 0.26.0 and against 0.26.3, in both directions.
- **R3-1:** re-run on 0.26.6.
- **`pack index verify` speed:** 0.26.0 against 0.26.1.

The scripts and every result are in [`admin/research/builds-0-26-x-2026-10-28/`](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/builds-0-26-x-2026-10-28).

## Open findings, for the CLI team {#open}

| # | Severity | In | Finding | Page |
|---|---|---|---|---|
| **BR-1** | **high** | every build tested, 0.26.0 to 0.26.6 | one push of more than 100 commits uploads only the newest 100; the host's history has a gap that later pushes never fill, a fresh clone's `fsck` fails, and merges across it conflict on everything | [0.26.6](../builds/0-26-6.md#br-1) |
| **BR-2** | medium | 0.26.5, opt-in | `--merge lines` can merge cleanly where `git merge-file` reports a conflict, when the changed lines repeat (2 in 4,544 code-like merges) | [0.26.5](../builds/0-26-5.md#br-2) |
| BR-3 | low | 0.26.5, opt-in | where both report a conflict, the blocks differ from Git's in 0.9% of code-like merges | [0.26.5](../builds/0-26-5.md#br-3) |
| **BR-4** | decision | 0.26.3 and later | a plain `pip install sgit-ai` installs the newest dev build, not the release; if the intent is that a plain install gets the release, dev builds must be pre-releases again | [0.26.3](../builds/0-26-3.md#br-4) |
| R3-1 | low | since 0.26.0 | after a compaction, `pack index verify` reports bad offsets for an archived pack an older client wrote; unchanged in 0.26.6 | [round 3](../research/pack-indexes-review-round-3.md#r3-1) |

*Reviewed by cli.build, cli.sgit.ai's build agent, on 28 October 2026. The roadmap these builds start on: [Git parity](../research/git-parity-roadmap.md).*

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/builds/index.html)*
