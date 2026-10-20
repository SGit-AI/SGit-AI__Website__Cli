# When NOT to use sgit, cli.sgit.ai

> The honest page: sgit's edges, stated plainly, plus the current roadmap gaps.

*Source: <https://cli.sgit.ai/docs/limitations.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/limitations.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# When NOT to use sgit

Every tool earns trust faster by stating its edges. Here are sgit's, plainly.

## Don't use sgit if…

- **You need a secrets manager.** sgit refuses to commit `.env` files, `.netrc`, private keys and friends, deliberately. Use a purpose-built secrets manager for credentials; use sgit for documents, data, and working files.
- **You need long-term API stability guarantees today.** sgit is in beta: it powers production workflows daily and the vault format is versioned (`sgit migrate` handles upgrades), but commands and flags can still evolve between minor versions. Keep `sgit vault backup` archives of anything precious.
- **You need partial commits.** There is no staging area, a commit snapshots the whole folder. If your workflow depends on committing three of seven changed files, sgit will fight you (use branches instead, or split folders into separate vaults).
- **Your data is huge binaries that change constantly.** Large files work (they're chunk-uploaded past a ~4 MB threshold), but sgit is built for working sets of documents and code-sized files, not video archives. Storage is versioned: history keeps old ciphertext around until pruned.
- **You want the server to do things with your data.** Zero knowledge cuts both ways: the server cannot index, search, preview, or process your content. All intelligence lives client-side. That is the point.
- **You lose keys.** There is no password reset, no recovery, no back door. That's a feature, but only if your key management is real. Password manager, plus `sgit vault backup --include-key` somewhere safe.

## Current gaps (roadmap, honestly)

- **Commit author attribution** is not yet recorded, in multi-agent vaults, per-agent identity currently comes from branch IDs, not signed authorship. Signature slots exist in the format; population is planned work.
- **Merge drivers** are whole-file three-way. Structured merges (JSON-aware, union) are designed but not yet shipped.
- **Bare clones** (`clone --bare`) are incomplete.
- **Partial clones have two edges.** A folder renamed by someone else silently leaves a scoped clone's scope, and a pull will not warn; re-clone or widen to the new name. And a scoped clone cannot see objects missing elsewhere in the vault, so `sgit check fsck`, `sgit dev dump`, `sgit publish` and `sgit vault move` need a full clone. See [Partial clones](../docs/partial-clones.md).
- **A partial clone is not an access boundary.** `--path` decides what is downloaded, not what can be read: the clone holds the vault key, and `sgit fetch <folder>` widens it to any folder. To keep agents out of each other's memory, give each its own vault. See [Self-hosting a vault server for agents](../docs/self-host-for-agents.md).
- **The full CLI reference** on this site is still being wired to its generator (it will be produced from the CLI's own argument parser on every release, so it can never go stale).

## What PKI does not do yet

[Keypairs](../docs/pki.md) ship and work, keygen, export, import, sign, verify, encrypt, decrypt all round-trip on v0.15.0. The layer around them is thinner than the primitives:

- **No revocation, expiry or rotation workflow.** No CRL, no `sgit pki revoke`. A compromised private key means generating a new pair and redistributing the bundle out of band, by hand.
- **No directory and no web of trust.** Verifying that a fingerprint belongs to who you think is entirely your problem, compare out of band, as with SSH host keys.
- **Lane addressing is not wired end to end.** The intended model is `append_token = H(public key)`, so a sender derives your [message lane](../docs/vault-messaging.md) address from the key you published. The server side ships; no shipped command emits that token, so today you agree one out of band. Details and the interim recipe are in the [addressing note](../docs/vault-messaging.md#addressing).
- **Only the first mode is built.** Signing and encrypting files, plus the append transport. The richer modes (group addressing, key discovery, delegated capability) are designs, not code.

Said plainly because the alternative is worse: an agent that reads an over-claiming page will build on a step that does not exist, and only find out at runtime.

If one of these gaps blocks you, say so on [GitHub](https://github.com/SGit-AI/SGit-AI__CLI/issues), real usage reports move the roadmap.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/limitations.html)*
