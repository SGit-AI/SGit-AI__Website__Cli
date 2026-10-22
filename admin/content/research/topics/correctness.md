---
title: Found in daily use
summary: The bugs that agents and people hit while using sgit every day, each traced to its cause in the code, with what was fixed and what is still open.
section: topics
order: 7
question: What broke when sgit was used for real, why, and is it fixed?
articles: [pack-mode-four-rounds]
---

# Found in daily use

**The question.** sgit is used every day by a team of agents on shared vaults. What broke under that use, what was the cause in the code, and what is fixed? These documents are the record, kept with the mistakes visible.

## Where it stands

| | Status | Where it is said |
|---|---|---|
| `sgit pull` silently discarded uncommitted edits to tracked files | **fixed** 3 October | [The fix](/research/pull-discarded-uncommitted-edits.html) |
| Branches did not work end to end; merge commits made by pull were unsigned | **fixed** for 0.21.0, with 22 unit and 5 integration tests | [Branches and the test suite](/research/branches-and-test-suite-review.html) |
| The issues of 14 October, each traced to its cause | **fixed** in part; the rest named | [Issues of 14 October](/research/sgit-issues-2026-10-14.html) |
| Paths with characters outside a narrow set give one vault two roots | **open** as of 13 October | [Refuse, don't rewrite](/research/non-ascii-paths-refuse-dont-rewrite.html) |
| Pack mode before release: data loss in compaction (a branch-only push, racing and aborted compactions), a failed first push dropping the root commit, `sgit tag create` failing on a pack vault | **fixed** in 0.24.0; found and reproduced by a second agent, fixed by the CLI team with a test each | [the four rounds](/articles/pack-mode-four-rounds.html) |

!topic correctness
