# Found in daily use, cli.sgit.ai

> The bugs that agents and people hit while using sgit every day, each traced to its cause in the code, with what was fixed and what is still open.

*Source: <https://cli.sgit.ai/research/topics/correctness.html> · generated from the same content as the page, so the two cannot drift.*

---
# Found in daily use

**The question.** sgit is used every day by a team of agents on shared vaults. What broke under that use, what was the cause in the code, and what is fixed? These documents are the record, kept with the mistakes visible.

## Where it stands

| | Status | Where it is said |
|---|---|---|
| `sgit pull` silently discarded uncommitted edits to tracked files | **fixed** 3 October | [The fix](../../research/pull-discarded-uncommitted-edits.md) |
| Branches did not work end to end; merge commits made by pull were unsigned | **fixed** for 0.21.0, with 22 unit and 5 integration tests | [Branches and the test suite](../../research/branches-and-test-suite-review.md) |
| The issues of 14 October, each traced to its cause | **fixed** in part; the rest named | [Issues of 14 October](../../research/sgit-issues-2026-10-14.md) |
| Paths with characters outside a narrow set give one vault two roots | **open** as of 13 October | [Refuse, don't rewrite](../../research/non-ascii-paths-refuse-dont-rewrite.md) |

## The research documents, newest first

- [Response to "sgit issues found on 14 October 2026", and the comms-vault performance report](../../research/sgit-issues-2026-10-14.md): The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same push and what was left open.
- [AC-L-001 / TM-R36 — characters outside `[a-zA-Z0-9/\_.- ]` in paths: what really happens](../../research/non-ascii-paths-refuse-dont-rewrite.md): Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting.
- [Branches check, test performance, test quality — 8 Oct 2026](../../research/branches-and-test-suite-review.md): An end-to-end check found that branches did not work. What was fixed behind it, the tests that now cover it, and a review of the test suite's speed and quality.
- [Fix — `sgit pull` silently discarded uncommitted edits to tracked files](../../research/pull-discarded-uncommitted-edits.md): sgit pull silently discarded uncommitted edits to tracked files. The root cause, and the fix: git's rules for the working tree, applied before any write.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/correctness.html)*
