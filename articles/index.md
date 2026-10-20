# Research, cli.sgit.ai

> Articles from the sgit CLI team, newest first: measurements, designs, reviews, decisions and fixes, each taking one topic as far as the evidence goes, with its source in the CLI repository.

*Source: <https://cli.sgit.ai/articles/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Research

The CLI team's articles, newest first. Each takes **one topic, one implementation or one idea** as far as the evidence goes: a measurement on a real vault, a design and the review that corrected it, a bug traced to its cause. They are, in the words of [the brief](../briefs/index.md), "our new generation of briefs", and this is where they are captured first.

The first 23 were written in the CLI repository between 2 and 16 October 2026 (`team/humans/dinis_cruz/claude-code-web/`) and are published here as written, each with its source path and commit. The *kind* on each card says what it is worth: a **measurement** is numbers from a run; a **design**, **plan** or **analysis** is a proposal, not a shipped feature, unless it says so; a **fix** or **finding** names the code.

- [sgit is a standard, not a server: everything in a vault is one hash away](../articles/sgit-is-a-standard-one-hash-away.md): A vault is a set of files laid out by a convention, every immutable object named by the hash of its own ciphertext, so the server is the least interesting part and anything in the path can cache blindly.
- [Response to "Scion and sgit" (newsroom.sgit.ai, article No. 141, v1.0.0)](../articles/response-to-scion-and-sgit.md): The CLI team's response to the newsroom's "Scion and sgit" article: what it gets right, the three factual errors, and the measurements from a 35k-object vault the article should have carried.
- [One vault, ten agents, 35,000 objects: what sgit does when the repository is big and the clients are many](../articles/one-vault-ten-agents-measured.md): What sgit does when the repository is big and the clients are many: the comms vault, 35,000 encrypted objects and ten agents, cloned eight ways and measured from a cloud sandbox.
- [Response to "sgit issues found on 14 October 2026", and the comms-vault performance report](../articles/sgit-issues-2026-10-14.md): The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same push and what was left open.
- [Security CI: a dedicated pipeline, and an AI review that can break the build](../articles/security-ci-and-ai-review.md): A dedicated security pipeline on every pull request, and a keyless AI security review that can break the build on anything new: why, how it is wired, and what it costs per reviewed change.
- [AC-L-001 / TM-R36 — characters outside `[a-zA-Z0-9/\_.- ]` in paths: what really happens](../articles/non-ascii-paths-refuse-dont-rewrite.md): Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting.
- [`sgit serve`: container first. Options map and spike results](../articles/sgit-serve-container-first.md): The decision to run the SG/Send container image rather than re-implement the server: the runtimes supported (including Apple's container and Podman), the spike results, and phase 1 as built.
- [`sgit serve`: running a vault locally — research and plan](../articles/sgit-serve-running-a-vault-locally.md): How to run a vault locally: the vault server's API inventory, the browser modes, when TLS is and is not needed, and how much plumbing sgit would need.
- [Case study — a tool-assisted security review of sgit-ai 0.21.0 (round 1)](../articles/security-review-case-study.md): What each tool found in the round-1 security review of sgit-ai 0.21.0, with counts and cost: the skill vetting, the derived graph, 270 function records, 68 STRIDE threats and the insider overlay.
- [Threat-modeling tools for an agent-driven review — Matt Adams' stack, the classics, and the house method](../articles/threat-modeling-tools.md): Threat-modeling tools for an agent-driven review: Matt Adams' stack (STRIDE GPT, the insider-threat model), the classics, and the house method, with the agent itself named as an actor.
- [Agent skills for security review — what exists, what it would do here](../articles/security-review-skills.md): Agent skills for security review, each checked at its source, ranked by whether it brings a method, a tool with deterministic output, or vets the other skills, against this code base.
- [Plan — the next security review of sgit-ai, with skills, and the review graphs it produces](../articles/security-review-plan.md): The plan for a tool-assisted, data-producing security review of one slice of sgit-ai: the code the zero-knowledge guarantee and the trust boundaries live in.
- [Sealed files — a second encryption layer on top of a vault](../articles/sealed-files-layer.md): A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH P-256, HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review.
- [Native PKI vault mode — architecture map](../articles/native-pki-vault-mode.md): An architecture map for a second vault mode built on key pairs from the start, revised twice after review: sequence-number pinning, frozen hosts, concurrent writers.
- [Read and write keys as PKI — design analysis](../articles/read-write-keys-as-pki.md): Are the read key and the write key really a public and a private key? Half right: the write key should become a signing key, and the read key cannot become a public key. What that would take.
- [Branches check, test performance, test quality — 8 Oct 2026](../articles/branches-and-test-suite-review.md): An end-to-end check found that branches did not work. What was fixed behind it, the tests that now cover it, and a review of the test suite's speed and quality.
- [Possible future features, after 0.21.0](../articles/future-features-after-0-21.md): The git-parity and security ideas that are not in 0.21.0, what each would take and what it could break, starting from the constraint that a new commit field breaks older clients' signature checks.
- [Review: "Git security features → sgit: a one-way mapping](../articles/git-to-sgit-security-mapping.md): A review of the one-way map from git's security features to sgit, checked against the code: three corrections, one missing gap, and the four easy gaps closed for 0.21.0.
- [Compatibility matrix: sgit CLI × vault web UI × SG/Send API, across the integrity roll-out](../articles/compatibility-matrix-cli-web-ui-api.md): The CLI, the vault web UI and the SG/Send API across the integrity roll-out, step by step: what each version reads, writes and loses, under the rule that no client may break another still writing.
- [History integrity: what the three fixes would cost, and how to ship them without a `vault move`](../articles/history-integrity-cost-and-compatibility.md): What signature verification, ref monotonicity and 128-bit ids would cost, measured on a real vault, and how to ship all three without a vault move.
- [Partial clones — a folder scope and a history depth (6 Oct 2026)](../articles/partial-clones-scope-and-depth.md): Cloning just the folders an agent reads and writes, read and write, plus a shallow mode, without changing the full clone: the Merkle-spine idea and the measurements.
- [Fix — `sgit pull` silently discarded uncommitted edits to tracked files](../articles/pull-discarded-uncommitted-edits.md): sgit pull silently discarded uncommitted edits to tracked files. The root cause, and the fix: git's rules for the working tree, applied before any write.
- [Clone performance — the tree walk re-fetched shared sub-trees once per parent](../articles/clone-refetched-shared-subtrees.md): A clone stuck walking trees: the walk re-fetched shared sub-trees once per parent, 10,098 requests for 2,236 unique trees. The instrumented run and the fix.

## Publishing an article

Adding one file publishes it: `admin/content/articles/<slug>.md`, with a title, a date and a summary in its front matter. The contract is in `admin/content/articles/README.md`.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/articles/index.html)*
