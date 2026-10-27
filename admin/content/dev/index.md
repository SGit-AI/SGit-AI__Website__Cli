---
title: Dev packs
summary: Design packs to build from: a set of documents written for the agents and engineers who will implement something, with the problem, the decisions, the architecture, the protocols, the evidence measured for it and how it rolls out. A dev pack is a design, not a release; each says what is built and what is not.
section: devpacks
hub: true
---

# Dev packs

A dev pack is a design written for the people and agents who will build it:
- the problem and the decisions;
- the architecture and the protocols;
- the evidence measured for it;
- how it rolls out without breaking what already works.

It sits between [research](/research/index.html), which asks a question, and [the docs](/docs/index.html), which describe what has shipped. Every pack says what is built and what is not.

## Pack indexes for sgit {#pack-indexes}

The client that pushes a pack also pushes an index pack beside it: the head's map, one file per folder, the commit graph with generation numbers, cross-references, and for each commit only what it changed. Readers stop walking trees, unpacking objects they never read, and downloading folders they do not want. **No gate:** clients up to 0.25.0 never see index packs. **Shipped in [sgit-ai 0.26.0](/docs/update-to-0-26-0.html)** on 27 October, Phases 1 to 3 ([the story](/articles/pack-indexes-shipped.html)); Phase 4 is not built. Written on 26 October 2026 for the sgit CLI team, from four measured articles: [indexes in the pack](/articles/indexes-in-the-pack.html), [a vault is already a graph](/articles/a-vault-is-already-a-graph.html), [indexes the writer pays for](/articles/indexes-the-writer-pays-for.html), and [every number](/research/graph-and-index-measurements-2026-10-26.html).

## Sealed vault keys for sgit {#sealed-vault-keys}

A vault key that arrives sealed, stays sealed on disk and is opened only inside a small KMS, with sgit split into four components under policies the agent cannot widen. **Opt-in:** with nothing switched on, sgit runs as 0.24.0 does. Written on 24 October 2026, from the requirements and the design published under [Keys, members and who may write](/research/topics/keys.html).

!list devpacks
