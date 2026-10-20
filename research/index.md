# Research, cli.sgit.ai

> The sgit CLI team's research, kept as written and grouped into topics: measurements on real vaults, designs and the reviews that corrected them, security reviews, and the bugs found in daily use, each with its source in the CLI repository.

*Source: <https://cli.sgit.ai/research/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Research

The CLI team's working documents, **published as written**: measurements on real vaults, designs and the reviews that corrected them, decisions, security reviews and the bugs found in daily use. Each one takes one question as far as the evidence went on the day it was written. They are the record, so they are not edited here; where one was wrong, a later document says so, usually above the mistake.

**Research is not the same as an article.** An [article](../articles/index.md) makes one argument for a reader, in the newsroom's format, and is written to be read start to finish. A research document is the work itself: tables, open questions, the plan that was later superseded. When a research thread produces an argument, it becomes an article, and the topic page links both.

## Topics

Each topic is one open question, with where it stands today: what is shipped, what is designed, what is absent.

- [Keys, members and who may write](../research/topics/keys.md): Should the read key and the write key become key pairs, can a vault have members who join and leave by a file each, and can a vault enforce who writes where? What is built, what is designed, and what is still a question.
- [History integrity and signatures](../research/topics/integrity.md): How sgit made a vault's history verifiable without a vault move: signed commits, a format gate, rewind detection, and the compatibility rule that a newer client must never break an older one still writing.
- [Big vaults and many agents](../research/topics/scale.md): What happens when a vault reaches 35,000 objects and ten agents use it every day: what a clone fetches, what each session costs, which fixes came from measuring it, and why the server can stay simple.
- [How a vault takes writes](../research/topics/write-path.md): One commit per change is right for documents and wrong for a stream. Copy-on-write, a write-ahead append lane folded into signed commits, and a vault in one zip file: what sgit already does, and what is proposed.
- [Running a vault locally](../research/topics/serve.md): How to run a working vault, UI and API, on your own machine: the research into the server's API, the decision to run the SG/Send container rather than re-implement it, and the runtimes sgit supports.
- [Reviewing sgit's security with tools and agents](../research/topics/security-review.md): A tool-assisted security review of the code the zero-knowledge guarantee lives in: which agent skills and threat-modelling tools were worth running, what each found, and a CI pipeline where an AI review can break the build.
- [Found in daily use](../research/topics/correctness.md): The bugs that agents and people hit while using sgit every day, each traced to its cause in the code, with what was fixed and what is still open.

## Every document, newest first

- [Keys the way git does them, PKI access to a vault, and copy-on-write: what is already published, and what is not](../research/keys-pki-copy-on-write-coverage-map.md): Before writing two articles, a map of what is already published on keys the way git does them, PKI access to a vault and copy-on-write: seven questions from the memo, where each stands, the facts the articles must not get wrong, and seven code questions for the thread.
- [Response to "Scion and sgit" (newsroom.sgit.ai, article No. 141, v1.0.0)](../research/response-to-scion-and-sgit.md): The CLI team's response to the newsroom's "Scion and sgit" article: what it gets right, the three factual errors, and the measurements from a 35k-object vault the article should have carried.
- [Response to "sgit issues found on 14 October 2026", and the comms-vault performance report](../research/sgit-issues-2026-10-14.md): The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same push and what was left open.
- [Security CI: a dedicated pipeline, and an AI review that can break the build](../research/security-ci-and-ai-review.md): A dedicated security pipeline on every pull request, and a keyless AI security review that can break the build on anything new: why, how it is wired, and what it costs per reviewed change.
- [AC-L-001 / TM-R36 — characters outside `[a-zA-Z0-9/\_.- ]` in paths: what really happens](../research/non-ascii-paths-refuse-dont-rewrite.md): Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting.
- [`sgit serve`: container first. Options map and spike results](../research/sgit-serve-container-first.md): The decision to run the SG/Send container image rather than re-implement the server: the runtimes supported (including Apple's container and Podman), the spike results, and phase 1 as built.
- [`sgit serve`: running a vault locally — research and plan](../research/sgit-serve-running-a-vault-locally.md): How to run a vault locally: the vault server's API inventory, the browser modes, when TLS is and is not needed, and how much plumbing sgit would need.
- [Case study — a tool-assisted security review of sgit-ai 0.21.0 (round 1)](../research/security-review-case-study.md): What each tool found in the round-1 security review of sgit-ai 0.21.0, with counts and cost: the skill vetting, the derived graph, 270 function records, 68 STRIDE threats and the insider overlay.
- [Threat-modeling tools for an agent-driven review — Matt Adams' stack, the classics, and the house method](../research/threat-modeling-tools.md): Threat-modeling tools for an agent-driven review: Matt Adams' stack (STRIDE GPT, the insider-threat model), the classics, and the house method, with the agent itself named as an actor.
- [Agent skills for security review — what exists, what it would do here](../research/security-review-skills.md): Agent skills for security review, each checked at its source, ranked by whether it brings a method, a tool with deterministic output, or vets the other skills, against this code base.
- [Plan — the next security review of sgit-ai, with skills, and the review graphs it produces](../research/security-review-plan.md): The plan for a tool-assisted, data-producing security review of one slice of sgit-ai: the code the zero-knowledge guarantee and the trust boundaries live in.
- [Sealed files — a second encryption layer on top of a vault](../research/sealed-files-layer.md): A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH P-256, HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review.
- [Native PKI vault mode — architecture map](../research/native-pki-vault-mode.md): An architecture map for a second vault mode built on key pairs from the start, revised twice after review: sequence-number pinning, frozen hosts, concurrent writers.
- [Read and write keys as PKI — design analysis](../research/read-write-keys-as-pki.md): Are the read key and the write key really a public and a private key? Half right: the write key should become a signing key, and the read key cannot become a public key. What that would take.
- [Branches check, test performance, test quality — 8 Oct 2026](../research/branches-and-test-suite-review.md): An end-to-end check found that branches did not work. What was fixed behind it, the tests that now cover it, and a review of the test suite's speed and quality.
- [Possible future features, after 0.21.0](../research/future-features-after-0-21.md): The git-parity and security ideas that are not in 0.21.0, what each would take and what it could break, starting from the constraint that a new commit field breaks older clients' signature checks.
- [Review: "Git security features → sgit: a one-way mapping](../research/git-to-sgit-security-mapping.md): A review of the one-way map from git's security features to sgit, checked against the code: three corrections, one missing gap, and the four easy gaps closed for 0.21.0.
- [Compatibility matrix: sgit CLI × vault web UI × SG/Send API, across the integrity roll-out](../research/compatibility-matrix-cli-web-ui-api.md): The CLI, the vault web UI and the SG/Send API across the integrity roll-out, step by step: what each version reads, writes and loses, under the rule that no client may break another still writing.
- [History integrity: what the three fixes would cost, and how to ship them without a `vault move`](../research/history-integrity-cost-and-compatibility.md): What signature verification, ref monotonicity and 128-bit ids would cost, measured on a real vault, and how to ship all three without a vault move.
- [Partial clones — a folder scope and a history depth (6 Oct 2026)](../research/partial-clones-scope-and-depth.md): Cloning just the folders an agent reads and writes, read and write, plus a shallow mode, without changing the full clone: the Merkle-spine idea and the measurements.
- [Fix — `sgit pull` silently discarded uncommitted edits to tracked files](../research/pull-discarded-uncommitted-edits.md): sgit pull silently discarded uncommitted edits to tracked files. The root cause, and the fix: git's rules for the working tree, applied before any write.
- [Clone performance — the tree walk re-fetched shared sub-trees once per parent](../research/clone-refetched-shared-subtrees.md): A clone stuck walking trees: the walk re-fetched shared sub-trees once per parent, 10,098 requests for 2,236 unique trees. The instrumented run and the fix.

## Where these come from

The CLI repository, `team/humans/dinis_cruz/claude-code-web/MM/DD/`, written by the CLI team's agents (Claude Code sessions) for Dinis Cruz between 2 and 20 October 2026. `admin/build/import_cli_research.py` copies them here with a front matter and nothing else; each page names its source file, commit and branch. This import was taken from commit `5473571` on the CLI's working branch `claude/charming-babbage-5hzcxq`, which holds everything on `dev` plus the documents of 16 and 20 October that were not yet merged when they were published here.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/research/index.html)*
