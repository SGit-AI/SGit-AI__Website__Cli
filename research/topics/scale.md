# Big vaults and many agents, cli.sgit.ai

> What happens when a vault reaches 35,000 objects and ten agents use it every day: what a clone fetches, what each session costs, which fixes came from measuring it, and why the server can stay simple.

*Source: <https://cli.sgit.ai/research/topics/scale.html> · generated from the same content as the page, so the two cannot drift.*

---
# Big vaults and many agents

**The question.** The comms vault grew from 18,720 objects on 6 October to 35,423 on 14 October, used by ten agents and one person. What does a clone, a pull and a session cost at that size, where does the time go, and what can be cached by anything in the path because the server cannot read it?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| The tree walk that re-fetched shared sub-trees once per parent | **fixed** (2 October) | [Clone re-fetched shared sub-trees](../../research/clone-refetched-shared-subtrees.md) |
| Partial clones: a folder scope (`--path`) and a history depth (`--depth`) | **shipped** in 0.18.0 | [Partial clones](../../docs/partial-clones.md), [the design](../../research/partial-clones-scope-and-depth.md) |
| Batched blob downloads, the far-behind sweep, large files without S3 | **fixed**, as the response of 14 October records | [Issues of 14 October](../../research/sgit-issues-2026-10-14.md) |
| The 35,000-object vault, cloned eight ways and served from local disk | **measured**, 16 October | [Response to "Scion and sgit"](../../research/response-to-scion-and-sgit.md), [the article](../../articles/one-vault-ten-agents-measured.md) |
| Every immutable object named by the hash of its ciphertext, so any cache can hold it | **shipped** (the `-imm-` naming) | [the article](../../articles/sgit-is-a-standard-one-hash-away.md) |
| A vault read as one zip instead of thousands of requests | **proposed**; the bundles are already written by `sgit publish --bundles` | [the article](../../articles/a-vault-in-one-file.md) |

## Articles from this topic

- [One vault, ten agents, 35,000 objects: what sgit does when the repository is big and the clients are many](../../articles/one-vault-ten-agents-measured.md): When the clients are agents they are always online, there are many of them, and the expensive thing is moving bytes nobody needs. Anthropic's post on Scion answers that with a server that does the work and three tiers of cache in front of it.
- [sgit is a standard, not a server: everything in a vault is one hash away](../../articles/sgit-is-a-standard-one-hash-away.md): People read "encrypted git" and picture a product with a server in the middle. There is a server, and it is the least interesting part. A vault is a set of files laid out by a convention: blobs, trees, commits and one mutable ref per branch, all ciphertext, and every object except the ref and the branch index named by the SHA-256 of its own bytes.
- [A vault in one file: native zip support for sgit, where it wins, where it loses, and what already exists](../../articles/a-vault-in-one-file.md): A vault is files and folders, so it can be a zip. Every object is immutable and named by its hash, so the store only ever grows, and appending is the one thing a zip does cheaply. I asked how much of that already exists, and the…
- [A pack per push: git's packfiles, applied to an encrypted vault, with no server change](../../articles/a-pack-per-push.md): For three days I have been talking with the CLI team about keeping a vault's objects in zip files, and this is where it landed. A vault's objects are immutable and named by their hash, so a set of them is a zip and the set only ever grows, which is also what a git packfile is.

## The research documents, newest first

- [Spec: pack mode for sgit (CLI-only, packs-only vaults, no server change)](../../research/pack-mode-spec.md): The specification for pack mode: every push writes one zip pack, a snapshot pack compacts them, nothing is deleted, large packs go straight to S3 by presigned URL, and a gated packs-only vault needs no server change. Commands,…
- [Response to "Scion and sgit" (newsroom.sgit.ai, article No. 141, v1.0.0)](../../research/response-to-scion-and-sgit.md): The CLI team's response to the newsroom's "Scion and sgit" article: what it gets right, the three factual errors, and the measurements from a 35k-object vault the article should have carried.
- [Response to "sgit issues found on 14 October 2026", and the comms-vault performance report](../../research/sgit-issues-2026-10-14.md): The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same push and what was left open.
- [Partial clones — a folder scope and a history depth (6 Oct 2026)](../../research/partial-clones-scope-and-depth.md): Cloning just the folders an agent reads and writes, read and write, plus a shallow mode, without changing the full clone: the Merkle-spine idea and the measurements.
- [Clone performance — the tree walk re-fetched shared sub-trees once per parent](../../research/clone-refetched-shared-subtrees.md): A clone stuck walking trees: the walk re-fetched shared sub-trees once per parent, 10,098 requests for 2,236 unique trees. The instrumented run and the fix.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/scale.html)*
