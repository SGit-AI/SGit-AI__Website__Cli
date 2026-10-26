---
title: Big vaults and many agents
summary: What happens when a vault reaches 35,000 objects and ten agents use it every day: what a clone fetches, what each session costs, which fixes came from measuring it, and why the server can stay simple.
section: topics
order: 3
question: What does sgit cost when the vault is big and the clients are many, and where does the time go?
articles: [a-vault-is-already-a-graph, indexes-in-the-pack, pack-mode-four-rounds, is-there-any-overhead, one-vault-ten-agents-measured, sgit-is-a-standard-one-hash-away, a-vault-in-one-file, a-pack-per-push]
---

# Big vaults and many agents

**The question.** The comms vault grew from 18,720 objects on 6 October to 35,423 on 14 October, used by ten agents and one person. What does a clone, a pull and a session cost at that size, where does the time go, and what can be cached by anything in the path because the server cannot read it?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| The tree walk that re-fetched shared sub-trees once per parent | **fixed** (2 October) | [Clone re-fetched shared sub-trees](/research/clone-refetched-shared-subtrees.html) |
| Partial clones: a folder scope (`--path`) and a history depth (`--depth`) | **shipped** in 0.18.0 | [Partial clones](/docs/partial-clones.html), [the design](/research/partial-clones-scope-and-depth.html) |
| Batched blob downloads, the far-behind sweep, large files without S3 | **fixed**, as the response of 14 October records | [Issues of 14 October](/research/sgit-issues-2026-10-14.html) |
| The 35,000-object vault, cloned eight ways and served from local disk | **measured**, 16 October | [Response to "Scion and sgit"](/research/response-to-scion-and-sgit.html), [the article](/articles/one-vault-ten-agents-measured.html) |
| Every immutable object named by the hash of its ciphertext, so any cache can hold it | **shipped** (the `-imm-` naming) | [the article](/articles/sgit-is-a-standard-one-hash-away.html) |
| A vault read as one zip instead of thousands of requests | **shipped** as pack mode in 0.24.0: a clone is the snapshot plus the commit packs, 3 or 4 requests (8.1 s against 28.6 s on a 2,087-object vault; 25 s against 3½ minutes on the comms vault's history). Scoped clones still take the packs whole | [release notes](/docs/update-to-0-24-0.html), [measurements](/research/pack-mode-round-trip-measured.html), [the article](/articles/a-pack-per-push.html) |
| Large vaults: the cost of a command follows the change, not the vault (linear and incremental tree builds, flat and scan caches) | **shipped** in 0.25.0 | [Release notes](/docs/update-to-0-25-0.html), [indexes and caches after 0.25.0](/research/indexes-and-caches-review.html) |
| Indexes carried with the packs and assembled locally into SQLite; packs read in place; one folder of a pack vault in one ranged read | **proposed**, 26 October; nothing built | [The architecture](/research/pack-carried-indexes-architecture.html), [the review, measured](/articles/indexes-in-the-pack.html) |
| A vault's graph as triples, and which graph engines Python can run locally | **measured**, 26 October: generation numbers answer a merge base in 0.1 ms; a graph engine as an optional view | [the article](/articles/a-vault-is-already-a-graph.html) |

!topic scale
