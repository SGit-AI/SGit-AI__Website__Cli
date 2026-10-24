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

## Sealed vault keys for sgit {#sealed-vault-keys}

A vault key that arrives sealed, stays sealed on disk and is opened only inside a small KMS, with sgit split into four components under policies the agent cannot widen. **Opt-in:** with nothing switched on, sgit runs as 0.24.0 does. Written on 24 October 2026, from the requirements and the design published under [Keys, members and who may write](/research/topics/keys.html).

!list devpacks
