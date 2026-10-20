---
title: Security model
summary: sgit's zero-knowledge security model, precisely stated: the crypto stack, what the server can and cannot see, key strength, and the open security process.
section: security
order: 1
moved_from: https://sgit.ai/security/index.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Security model

Zero knowledge, precisely stated: every file is encrypted on your machine before upload, keys are derived locally from your vault key, and the server stores ciphertext under opaque identifiers. This page tells you exactly what that means, including what the server *can* see.

## What the server sees, and never sees

| The server never sees | The server does see |
|---|---|
| File contents (encrypted client-side, AES-256-GCM) | The vault ID (an opaque random identifier) |
| Filenames and folder structure | Encrypted object sizes |
| Commit messages and branch names | Timing of reads and writes |
| Your vault key or any derived key | Approximate activity volume (object counts) |

We state the right-hand column deliberately. Traffic analysis of sizes and timing is a real (if narrow) channel, and pretending otherwise would be marketing, not security.

## The crypto stack

| Layer | Construction |
|---|---|
| Content encryption | AES-256-GCM, 12-byte IV, 16-byte tag, byte-compatible with the browser's Web Crypto API |
| Key derivation from the vault key | PBKDF2-HMAC-SHA256, 600,000 iterations, distinct per-vault salts for read and write keys |
| Purpose-specific keys | HKDF-SHA256, per-file keys and a structure key, one-way derived from the read key |
| Server-side identifiers | HMAC-SHA256-derived opaque IDs, the server addresses files it cannot name |
| Object identity | Content-addressed: `obj-cas-imm-<sha256-prefix>` over ciphertext, enabling dedup without plaintext knowledge |

One precision note, because precision beats marketing: the key hierarchy derives a *structure key* (one-way from the read key) designed to separate access to vault metadata from access to file contents. Today, vault objects are encrypted under the read key, activating the structure-key split across structural objects is an in-progress, reviewed design change, and this page will say so when it lands, not before.

## Two key systems, and where each applies

Everything above describes the **symmetric** half, and it is the half that matters most: the vault key is symmetric, it is the root of the storage hierarchy, and every object in a vault is encrypted under a key derived one-way from it. If you only ever use sgit to sync your own files across your own machines, that is the whole system.

There is a second half. Layered on top is a **public-key** system, for the two things a shared symmetric key cannot express: **proving who wrote something**, and **encrypting to somebody who does not hold your vault key**. It is what makes [vault-to-vault messaging](/docs/vault-messaging.html) possible, a sender can encrypt to your published public key and drop the result into your vault without ever being able to read it.

|  | Vault key (symmetric) | Keypair (asymmetric) |
|---|---|---|
| What it is | One generated string: address, credential and encryption root | An encryption pair and a signing pair, generated locally |
| What it protects | Every object in the vault | Individual files addressed to a recipient, and signatures over them |
| Who holds it | Everyone who can open the vault | Private half: you alone. Public half: publish it freely |
| Answers | “Can this person open the vault?” | “Who wrote this?” and “Can only *they* read it?” |
| Where it lives on the server | Never, the server holds ciphertext only | Public keys at `bare/keys/key-rnd-imm-*`. Private keys never leave your machine |

The constructions, read out of `sgit pki keygen` on v0.15.0 rather than recalled: **RSA-OAEP 4096-bit** for encryption and **ECDSA P-256** for signing, with a hybrid envelope, RSA-OAEP wraps a per-message AES-256-GCM content key. Private keys are passphrase-protected at rest. The full lifecycle is on [the PKI page](/docs/pki.html).

**This section is new, and its absence had a cost.** Until now this page described the symmetric design and simply did not mention asymmetric cryptography, it never claimed PKI was absent, but it never said it was present either. An agent researching how to send a message between vaults read this page, concluded there was no public-key layer, and stopped looking. The capability had shipped; the sentence that would have pointed at it had not been written. Silence on a page like this one reads as denial.

## Key strength

Vault keys are generated, not chosen. A generated passphrase is 24 characters over a 36-symbol alphabet (about **124 bits of entropy** (3624 ≈ 2124), far beyond brute-force reach) before key derivation adds 600,000 rounds of PBKDF2-SHA256 on top. The key never travels to the server: it is the address, the credential, and the root of the encryption hierarchy in one string, and it stays on your machines.

**Consequence you should want:** there is no password reset. If you lose the vault key, nobody, including us, can recover the contents. Keep it in a password manager, and use `sgit vault backup` for belt-and-braces.

## Two implementations, one wire format

The sgit CLI and the SG/Vault browser client are independent implementations of the same encrypted wire format, kept interoperable through a versioned contract with test vectors. Every crypto operation must produce byte-for-byte identical output to the Web Crypto API given the same inputs, that requirement is enforced with mandatory test vectors, and it means a second, independent codebase continuously exercises the same format. (More on the browser side at [sgraph.ai](https://sgraph.ai).)

## Secrets safety by default

sgit is not a secrets manager, and it actively refuses to become an accidental one: files like `.env*`, `.netrc`, `.pgpass`, `.git-credentials` and private key files (`id_rsa`, …) are *always* excluded from commits, so a stray credential can't get swept into a vault snapshot.

## Open security process

- Open source under Apache-2.0, with a deliberately tiny dependency surface: two runtime dependencies.
- ~4,000 tests including mutation testing in CI and integration tests against a real server, no mocks.
- An internal security review series (twelve findings, each individually worked through and debriefed, covering key residency, IV determinism trade-offs, logging hygiene, and more) is being prepared for publication on this page.
- Found something? Report it via [GitHub](https://github.com/SGit-AI/SGit-AI__CLI/issues), security reports get priority.
- **Key exposed?** [The rotation runbook](https://sgit.ai/case-studies/exposed-vault-key.html), including a worked case study of the day this site's own vault key leaked, and what it cost to fix.

**Honesty note:** sgit is in beta (it powers production workflows daily, and the cryptography is conservative and standard (AES-GCM, PBKDF2, HKDF) nothing exotic). Still: read [when NOT to use sgit](/docs/limitations.html) before trusting it with anything critical.
