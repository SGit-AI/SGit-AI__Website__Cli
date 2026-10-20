# History integrity and signatures, cli.sgit.ai

> How sgit made a vault's history verifiable without a vault move: signed commits, a format gate, rewind detection, and the compatibility rule that a newer client must never break an older one still writing.

*Source: <https://cli.sgit.ai/research/topics/integrity.html> · generated from the same content as the page, so the two cannot drift.*

---
# History integrity and signatures

**The question.** A host that stores ciphertext could still replay, rewind or forge a branch's head, and every reader would follow. Can every reader check the history, with signatures, ref monotonicity and longer ids, without moving existing vaults and without breaking a client that is still writing on an older version?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Canonical (JCS) signing input, `author_key_id`, `check verify`, `signatures-required`, rewind detection, the shared branch index | **shipped** in 0.19.0 to 0.21.0 | [History integrity](../../docs/history-integrity.md), [Update to 0.21.0](../../docs/update-to-0-21-0.md) |
| The format gate: format 2, 128-bit ids, `--min-client` | **shipped** | [History integrity](../../docs/history-integrity.md), [`sgit vault format`](../../reference/vault.md#vault-format) |
| What each fix costs, measured on a real vault (verify 66 µs a commit) | **measured**, 7 October | [Cost and compatibility](../../research/history-integrity-cost-and-compatibility.md) |
| Every client version against the web UI and the API, step by step | **analysis**, 7 October | [Compatibility matrix](../../research/compatibility-matrix-cli-web-ui-api.md) |
| git's security features mapped onto sgit, with corrections | **review**; four gaps closed for 0.21.0 | [Git to sgit security mapping](../../research/git-to-sgit-security-mapping.md) |
| The ideas after 0.21.0, bounded by "a new commit field breaks older clients' signature checks" | **proposed** | [Future features](../../research/future-features-after-0-21.md) |

## The research documents, newest first

- [Possible future features, after 0.21.0](../../research/future-features-after-0-21.md): The git-parity and security ideas that are not in 0.21.0, what each would take and what it could break, starting from the constraint that a new commit field breaks older clients' signature checks.
- [Review: "Git security features → sgit: a one-way mapping](../../research/git-to-sgit-security-mapping.md): A review of the one-way map from git's security features to sgit, checked against the code: three corrections, one missing gap, and the four easy gaps closed for 0.21.0.
- [Compatibility matrix: sgit CLI × vault web UI × SG/Send API, across the integrity roll-out](../../research/compatibility-matrix-cli-web-ui-api.md): The CLI, the vault web UI and the SG/Send API across the integrity roll-out, step by step: what each version reads, writes and loses, under the rule that no client may break another still writing.
- [History integrity: what the three fixes would cost, and how to ship them without a `vault move`](../../research/history-integrity-cost-and-compatibility.md): What signature verification, ref monotonicity and 128-bit ids would cost, measured on a real vault, and how to ship all three without a vault move.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/integrity.html)*
