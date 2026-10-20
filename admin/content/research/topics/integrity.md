---
title: History integrity and signatures
summary: How sgit made a vault's history verifiable without a vault move: signed commits, a format gate, rewind detection, and the compatibility rule that a newer client must never break an older one still writing.
section: topics
order: 2
question: Can every reader check a vault's history, when the host could forge it and old clients are still writing?
articles: []
---

# History integrity and signatures

**The question.** A host that stores ciphertext could still replay, rewind or forge a branch's head, and every reader would follow. Can every reader check the history, with signatures, ref monotonicity and longer ids, without moving existing vaults and without breaking a client that is still writing on an older version?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Canonical (JCS) signing input, `author_key_id`, `check verify`, `signatures-required`, rewind detection, the shared branch index | **shipped** in 0.19.0 to 0.21.0 | [History integrity](/docs/history-integrity.html), [Update to 0.21.0](/docs/update-to-0-21-0.html) |
| The format gate: format 2, 128-bit ids, `--min-client` | **shipped** | [History integrity](/docs/history-integrity.html), [`sgit vault format`](/reference/vault.html#vault-format) |
| What each fix costs, measured on a real vault (verify 66 µs a commit) | **measured**, 7 October | [Cost and compatibility](/research/history-integrity-cost-and-compatibility.html) |
| Every client version against the web UI and the API, step by step | **analysis**, 7 October | [Compatibility matrix](/research/compatibility-matrix-cli-web-ui-api.html) |
| git's security features mapped onto sgit, with corrections | **review**; four gaps closed for 0.21.0 | [Git to sgit security mapping](/research/git-to-sgit-security-mapping.html) |
| The ideas after 0.21.0, bounded by "a new commit field breaks older clients' signature checks" | **proposed** | [Future features](/research/future-features-after-0-21.html) |

!topic integrity
