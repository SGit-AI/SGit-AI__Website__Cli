---
title: Reviewing sgit's security with tools and agents
summary: A tool-assisted security review of the code the zero-knowledge guarantee lives in: which agent skills and threat-modelling tools were worth running, what each found, and a CI pipeline where an AI review can break the build.
section: topics
order: 6
question: What does a security review look like when agents run it, and which tools find things the existing work did not?
articles: [pack-mode-four-rounds]
---

# Reviewing sgit's security with tools and agents

**The question.** sgit is operated by agents that hold vault keys. What does a security review of its key path look like when agents run it with published skills and tools, which of those find something the existing threat model did not, and how much of it can run on every pull request?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Agent skills for security review, each checked at its source and ranked | **research**, 11 October | [Security review skills](/research/security-review-skills.html) |
| Threat-modelling tools, with the agent itself named as an actor | **research**, 11 October | [Threat-modelling tools](/research/threat-modeling-tools.html) |
| The plan: one slice, five skills, three tools, joined to the register | **accepted** 11 October | [The plan](/research/security-review-plan.html) |
| Round 1 run on 0.21.0: 270 function records, 68 STRIDE threats, with counts per tool | **done** | [The case study](/research/security-review-case-study.html) |
| A security workflow on every pull request; an AI review that can fail it, keyless | **built**; the AI review is off until connected | [Security CI](/research/security-ci-and-ai-review.html) |
| Paths with characters outside a narrow set silently rewritten (AC-L-001) | **documented** 13 October, fix proposed | [Refuse, don't rewrite](/research/non-ascii-paths-refuse-dont-rewrite.html) |
| Pack mode reviewed before release by a second agent: a zip bomb, unverified member names, a gate that admitted older clients, and four ways compaction could strand a clone | **fixed** in 0.24.0, a test per finding, over four rounds on 21 and 22 October | [round 1](/research/pack-mode-verification-round-1.html), [2](/research/pack-mode-verification-round-2.html), [3](/research/pack-mode-verification-round-3.html), [4](/research/pack-mode-verification-round-4.html); [the story](/articles/pack-mode-four-rounds.html) |

!topic security-review
