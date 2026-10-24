# Dev packs, cli.sgit.ai

> Design packs to build from: a set of documents written for the agents and engineers who will implement something, with the problem, the decisions, the architecture, the protocols, the evidence measured for it and how it rolls out. A dev pack is a design, not a release; each says what is built and what is not.

*Source: <https://cli.sgit.ai/dev/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Dev packs

A dev pack is a design written for the people and agents who will build it:
- the problem and the decisions;
- the architecture and the protocols;
- the evidence measured for it;
- how it rolls out without breaking what already works.

It sits between [research](../research/index.md), which asks a question, and [the docs](../docs/index.md), which describe what has shipped. Every pack says what is built and what is not.

## Sealed vault keys for sgit {#sealed-vault-keys}

A vault key that arrives sealed, stays sealed on disk and is opened only inside a small KMS, with sgit split into four components under policies the agent cannot widen. **Opt-in:** with nothing switched on, sgit runs as 0.24.0 does. Written on 24 October 2026, from the requirements and the design published under [Keys, members and who may write](../research/topics/keys.md).

- [Sealed vault keys for sgit: a design pack](../dev/sealed-vault-keys/index.md): A design pack for the agents and engineers who will build sealed vault keys into sgit. A vault key arrives sealed (pki.sgit.ai's QR handover), stays sealed on disk and is opened only inside a small KMS. sgit is split into four components (cli, fs, net, kms), each under a Process Behaviour Policy enforced by the kernel and by mutual TLS. Everything is opt-in: with nothing switched on, sgit runs exactly as 0.24.0 does, one process with vault keys on disk, and sealed and plain clones of the same vault work side by side. Six documents: the problem and decisions, the architecture, the key flow and KMS protocol, the policies, the measured evidence, and compatibility and rollout.
- [Sealed vault keys, 01: architecture](../dev/sealed-vault-keys/01-architecture.md): The four components of a sealed-key sgit (cli, fs, net, kms), each with one job and its own policy, talking only over mutual TLS along three allowed edges with a session CA; the command flows; five deployment topologies from one VM to a platform-provided KMS; the launcher; and the refactor path in sgit, in which nothing changes for a clone that is not sealed.
- [Sealed vault keys, 02: the key flow and the KMS](../dev/sealed-vault-keys/02-sealed-key-flow-and-kms.md): The handover from one agent to another with a person as the transport, the input checks kept from pki.sgit.ai, what a sealed clone keeps on disk, the KMS protocol (init, public, unwrap, seal_to, destroy) with derived keys re-sealed to a one-time key, the checks in order, the measured costs, binding a remote KMS to its caller, where the private key lives and for how long, and what is not claimed.
- [Sealed vault keys, 03: process behaviour policies](../dev/sealed-vault-keys/03-process-behaviour-policy.md): Process Behaviour Policies, the Agent Behaviour Policy model applied to a process: mandate, grant, delta and barrier; why who enforces a policy decides whether it binds; fractal layers that can only narrow; the schema, hashed as canonical JSON; how each line is enforced, mostly by the kernel; hashing, signing and distribution from a hash the person supplies; learning a policy from traces; and a prompt-injection walkthrough. Policies apply to sealed sessions only; with none supplied, sgit runs as 0.24.0 does.
- [Sealed vault keys, 04: environment evidence](../dev/sealed-vault-keys/04-environment-evidence.md): Every probe and measurement behind the pack, taken on 24 October 2026 in a Claude agent workspace (a cloud session in a microVM): the environment, the article's claims checked against sgit 0.24.0, memory (memfd_secret, keyrings, freezing), process isolation (users, capabilities, Landlock, namespaces), sgit's footprint under strace, and the cost of mutual TLS between components. Root inside the VM is the platform's design, not a finding; re-run the probes before relying on them elsewhere.
- [Sealed vault keys, 05: compatibility and rollout](../dev/sealed-vault-keys/05-compatibility-and-rollout.md): The rule that governs the whole pack: with nothing switched on, sgit behaves exactly as 0.24.0 does, one process with the vault key on disk, and every vault and agent keeps working unchanged. What must not change, how the sealed path is switched on per clone and never globally, why sealed and plain clones of one vault work side by side, what an older sgit sees, five rollout stages that test the new path in production beside the old one, rollback at every stage, and the tests that prove nothing broke.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/dev/index.html)*
