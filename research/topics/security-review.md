# Reviewing sgit's security with tools and agents, cli.sgit.ai

> A tool-assisted security review of the code the zero-knowledge guarantee lives in: which agent skills and threat-modelling tools were worth running, what each found, and a CI pipeline where an AI review can break the build.

*Source: <https://cli.sgit.ai/research/topics/security-review.html> · generated from the same content as the page, so the two cannot drift.*

---
# Reviewing sgit's security with tools and agents

**The question.** sgit is operated by agents that hold vault keys. What does a security review of its key path look like when agents run it with published skills and tools, which of those find something the existing threat model did not, and how much of it can run on every pull request?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Agent skills for security review, each checked at its source and ranked | **research**, 11 October | [Security review skills](../../research/security-review-skills.md) |
| Threat-modelling tools, with the agent itself named as an actor | **research**, 11 October | [Threat-modelling tools](../../research/threat-modeling-tools.md) |
| The plan: one slice, five skills, three tools, joined to the register | **accepted** 11 October | [The plan](../../research/security-review-plan.md) |
| Round 1 run on 0.21.0: 270 function records, 68 STRIDE threats, with counts per tool | **done** | [The case study](../../research/security-review-case-study.md) |
| A security workflow on every pull request; an AI review that can fail it, keyless | **built**; the AI review is off until connected | [Security CI](../../research/security-ci-and-ai-review.md) |
| Paths with characters outside a narrow set silently rewritten (AC-L-001) | **documented** 13 October, fix proposed | [Refuse, don't rewrite](../../research/non-ascii-paths-refuse-dont-rewrite.md) |

## The research documents, newest first

- [Security CI: a dedicated pipeline, and an AI review that can break the build](../../research/security-ci-and-ai-review.md): A dedicated security pipeline on every pull request, and a keyless AI security review that can break the build on anything new: why, how it is wired, and what it costs per reviewed change.
- [AC-L-001 / TM-R36 — characters outside `[a-zA-Z0-9/\_.- ]` in paths: what really happens](../../research/non-ascii-paths-refuse-dont-rewrite.md): Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting.
- [Case study — a tool-assisted security review of sgit-ai 0.21.0 (round 1)](../../research/security-review-case-study.md): What each tool found in the round-1 security review of sgit-ai 0.21.0, with counts and cost: the skill vetting, the derived graph, 270 function records, 68 STRIDE threats and the insider overlay.
- [Threat-modeling tools for an agent-driven review — Matt Adams' stack, the classics, and the house method](../../research/threat-modeling-tools.md): Threat-modeling tools for an agent-driven review: Matt Adams' stack (STRIDE GPT, the insider-threat model), the classics, and the house method, with the agent itself named as an actor.
- [Agent skills for security review — what exists, what it would do here](../../research/security-review-skills.md): Agent skills for security review, each checked at its source, ranked by whether it brings a method, a tool with deterministic output, or vets the other skills, against this code base.
- [Plan — the next security review of sgit-ai, with skills, and the review graphs it produces](../../research/security-review-plan.md): The plan for a tool-assisted, data-producing security review of one slice of sgit-ai: the code the zero-knowledge guarantee and the trust boundaries live in.
- [Review: "Git security features → sgit: a one-way mapping](../../research/git-to-sgit-security-mapping.md): A review of the one-way map from git's security features to sgit, checked against the code: three corrections, one missing gap, and the four easy gaps closed for 0.21.0.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/security-review.html)*
