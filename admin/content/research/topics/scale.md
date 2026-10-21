---
title: Big vaults and many agents
summary: What happens when a vault reaches 35,000 objects and ten agents use it every day: what a clone fetches, what each session costs, which fixes came from measuring it, and why the server can stay simple.
section: topics
order: 3
question: What does sgit cost when the vault is big and the clients are many, and where does the time go?
articles: [one-vault-ten-agents-measured, sgit-is-a-standard-one-hash-away, a-vault-in-one-file, a-pack-per-push]
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
| A vault read as one zip instead of thousands of requests | **proposed**; the bundles are already written by `sgit publish --bundles` | [the article](/articles/a-vault-in-one-file.html) |

!topic scale
