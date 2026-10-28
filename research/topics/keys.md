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
| Revoking a reader without rotating the key | **absent**; rotation is the rule today | [Key management](../../docs/key-management.md) |
| A vault key that arrives sealed, stays sealed on disk and opens only in memory: `sgit id`, `sgit agent`, `clone --sealed` | **proposed** 24 October; today the clear key is in `.sg_vault/local/vault_key` | [the article](../../articles/a-vault-key-that-never-lands.md) |
| A second factor without a server: passkey PRF and security-key `hmac-secret` as part of the key, a person as an agent's co-signer | **proposed** 24 October; passkey PRF already opens vaults on pki.sgit.ai | [the article](../../articles/a-second-factor-without-a-server.md) |

## Articles from this topic

- [A vault key that never lands: native PKI in sgit, so a key arrives sealed, stays sealed on disk and is opened only in memory](../../articles/a-vault-key-that-never-lands.md): pki.sgit.ai has made something work that I did not expect to feel this good. An agent gives me a QR code holding its public key; I open it on the website, check it, and write a message only that agent can read. Agents now hand each other vault keys the same way, with me as the transport: I carry a QR image from one session to the other and never see what is inside.
- [A second factor without a server: why an authenticator app's code cannot protect a vault, why a passkey or a security key can, and what the second factor is for an agent](../../articles/a-second-factor-without-a-server.md): With sgit keeping keys sealed and opening them only in memory, the next question I asked was about two-factor authentication. I have Google Authenticator on my phone, LastPass, passkeys, a YubiKey. Could sgit ask for one of them…
- [Keys the way git does them, and the way a vault could: what SSH actually checks, what a read key actually prevents, and a door per member](../../articles/keys-the-way-git-does-it.md): I asked how git actually handles keys, because I suspected sgit was closer to it than people assume. Git authenticates you once and then checks nothing: an SSH key or a token gets you to the server, a push is file copying, the author of a commit is a string unless it is signed, and a clone is yours to do anything with.
- [Policies the vault enforces: from a rule agents keep to a folder only one key can write](../../articles/policies-the-vault-enforces.md): On ruv.sgit the vault is the record of a policy, not its enforcer. RiskMandate writes the mandate, the grant, the gap and the barrier; ruv.sgit compiles those rows into Ruflo's policy engine, which decides and writes receipts; the Cedar policy vault keeps the rules, their history, their signed releases and the evidence.

## The research documents, newest first

- [Design 02: signing commits and tags with your own key, the way Git does it](../../research/git-parity-design-signing.md): Design 02: sign commits and tags with the SSH or GPG key you already have, as an optional second signature, and verify against your own allowed-signers file, the way Git leaves trust to the verifier. No gate. Not built.
- [Sealed vault keys: the requirements and the design, side by side](../../research/sealed-vault-keys-side-by-side.md): Two documents arrived on the same day about the same gap, a vault key that is sealed in transit and in clear at rest. One is a list of ten requirements from an agent that moves vault keys for a living; the other is cli.sgit.ai's design for native PKI in sgit.
- [Sealed vault keys in sgit: requirements](../../research/sealed-vault-keys-requirements.md): Requirements for sealed vault keys in sgit, from an agent that spent a fortnight moving vault keys between Dinis Cruz and many agent sessions, by paste and then by sealed QR code. The three places a vault key is still in clear on…
- [Keys the way git does them, PKI access to a vault, and copy-on-write: what is already published, and what is not](../../research/keys-pki-copy-on-write-coverage-map.md): Before writing two articles, a map of what is already published on keys the way git does them, PKI access to a vault and copy-on-write: seven questions from the memo, where each stands, the facts the articles must not get wrong,…
- [Sealed files — a second encryption layer on top of a vault](../../research/sealed-files-layer.md): A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH P-256, HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review.
- [Native PKI vault mode — architecture map](../../research/native-pki-vault-mode.md): An architecture map for a second vault mode built on key pairs from the start, revised twice after review: sequence-number pinning, frozen hosts, concurrent writers.
- [Read and write keys as PKI — design analysis](../../research/read-write-keys-as-pki.md): Are the read key and the write key really a public and a private key? Half right: the write key should become a signing key, and the read key cannot become a public key. What that would take.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/keys.html)*
