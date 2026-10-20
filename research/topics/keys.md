# Keys, members and who may write, cli.sgit.ai

> Should the read key and the write key become key pairs, can a vault have members who join and leave by a file each, and can a vault enforce who writes where? What is built, what is designed, and what is still a question.

*Source: <https://cli.sgit.ai/research/topics/keys.html> · generated from the same content as the page, so the two cannot drift.*

---
# Keys, members and who may write

**The question.** Today a vault has one secret: the vault key, from which a read key and a write key are derived. Every writer presents the same write key, so the server cannot tell writers apart, and a read key, once given, reads all history. Can a vault know who its members are, let them join and leave one at a time, and refuse a write from the wrong one, without the server ever reading anything?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Commits signed by each clone's own ECDSA P-256 key; `signatures-required` makes every client refuse an unsigned commit | **shipped** (0.19.0 and later) | [History integrity](../../docs/history-integrity.md) |
| `sgit pki`: RSA-4096 encryption pairs, ECDSA signing pairs, encrypt to a recipient, sign and verify | **shipped** | [Keys and signatures](../../docs/pki.md), [`sgit pki`](../../reference/pki.md) |
| The write key as a private signing key, with a writer set the server trusts | **designed**, not built | [Read and write keys as PKI](../../research/read-write-keys-as-pki.md) |
| A second vault mode built on two key pairs from the start, with sequence-number pinning | **designed**, revised twice after review | [Native PKI vault mode](../../research/native-pki-vault-mode.md) |
| Files sealed to named recipients on top of either mode | **designed** | [Sealed files](../../research/sealed-files-layer.md) |
| A door per member: one object holding the data key sealed to that member's key, outside history | **proposed**; the pieces exist separately | [the coverage map](../../research/keys-pki-copy-on-write-coverage-map.md), [the article](../../articles/keys-the-way-git-does-it.md) |
| A policy row (*key K may write `path/`*) refused by every honest client | **proposed** | [the article](../../articles/policies-the-vault-enforces.md) |
| Revoking a reader without rotating the key, or opening a vault with no key on disk | **absent**; rotation is the rule today | [Key management](../../docs/key-management.md) |

## Articles from this topic

- [Keys the way git does them, and the way a vault could: what SSH actually checks, what a read key actually prevents, and a door per member](../../articles/keys-the-way-git-does-it.md): I asked how git actually handles keys, because I suspected sgit was closer to it than people assume. Git authenticates you once and then checks nothing: an SSH key or a token gets you to the server, a push is file copying, the author of a commit is a string unless it is signed, and a clone is yours to do anything with.
- [Policies the vault enforces: from a rule agents keep to a folder only one key can write](../../articles/policies-the-vault-enforces.md): On ruv.sgit the vault is the record of a policy, not its enforcer. RiskMandate writes the mandate, the grant, the gap and the barrier; ruv.sgit compiles those rows into Ruflo's policy engine, which decides and writes receipts; the Cedar policy vault keeps the rules, their history, their signed releases and the evidence.

## The research documents, newest first

- [Keys the way git does them, PKI access to a vault, and copy-on-write: what is already published, and what is not](../../research/keys-pki-copy-on-write-coverage-map.md): Before writing two articles, a map of what is already published on keys the way git does them, PKI access to a vault and copy-on-write: seven questions from the memo, where each stands, the facts the articles must not get wrong,…
- [Sealed files — a second encryption layer on top of a vault](../../research/sealed-files-layer.md): A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH P-256, HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review.
- [Native PKI vault mode — architecture map](../../research/native-pki-vault-mode.md): An architecture map for a second vault mode built on key pairs from the start, revised twice after review: sequence-number pinning, frozen hosts, concurrent writers.
- [Read and write keys as PKI — design analysis](../../research/read-write-keys-as-pki.md): Are the read key and the write key really a public and a private key? Half right: the write key should become a signing key, and the read key cannot become a public key. What that would take.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/keys.html)*
