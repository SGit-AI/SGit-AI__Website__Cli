---
title: Keys, members and who may write
summary: Should the read key and the write key become key pairs, can a vault have members who join and leave by a file each, and can a vault enforce who writes where? What is built, what is designed, and what is still a question.
section: topics
order: 1
question: Can a vault know who its members are, and refuse a write from the wrong one, without the server reading anything?
articles: [keys-the-way-git-does-it, policies-the-vault-enforces]
---

# Keys, members and who may write

**The question.** Today a vault has one secret: the vault key, from which a read key and a write key are derived. Every writer presents the same write key, so the server cannot tell writers apart, and a read key, once given, reads all history. Can a vault know who its members are, let them join and leave one at a time, and refuse a write from the wrong one, without the server ever reading anything?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Commits signed by each clone's own ECDSA P-256 key; `signatures-required` makes every client refuse an unsigned commit | **shipped** (0.19.0 and later) | [History integrity](/docs/history-integrity.html) |
| `sgit pki`: RSA-4096 encryption pairs, ECDSA signing pairs, encrypt to a recipient, sign and verify | **shipped** | [Keys and signatures](/docs/pki.html), [`sgit pki`](/reference/pki.html) |
| The write key as a private signing key, with a writer set the server trusts | **designed**, not built | [Read and write keys as PKI](/research/read-write-keys-as-pki.html) |
| A second vault mode built on two key pairs from the start, with sequence-number pinning | **designed**, revised twice after review | [Native PKI vault mode](/research/native-pki-vault-mode.html) |
| Files sealed to named recipients on top of either mode | **designed** | [Sealed files](/research/sealed-files-layer.html) |
| A door per member: one object holding the data key sealed to that member's key, outside history | **proposed**; the pieces exist separately | [the coverage map](/research/keys-pki-copy-on-write-coverage-map.html), [the article](/articles/keys-the-way-git-does-it.html) |
| A policy row (*key K may write `path/`*) refused by every honest client | **proposed** | [the article](/articles/policies-the-vault-enforces.html) |
| Revoking a reader without rotating the key, or opening a vault with no key on disk | **absent**; rotation is the rule today | [Key management](/docs/key-management.html) |

!topic keys
