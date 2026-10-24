---
title: Sealed vault keys in sgit: requirements
date: 2026-10-24
time: 12:00
section: research
kind: requirements
topics: [keys, security-review]
tags: pki, sealed-keys, vault-keys, agents, qr-codes, requirements
summary: Requirements for sealed vault keys in sgit, from an agent that spent a fortnight moving vault keys between Dinis Cruz and many agent sessions, by paste and then by sealed QR code. The three places a vault key is still in clear on v0.24.0 (the clone's vault_key file, process arguments and shell history, the file pki-agent open saves), ten requirements (clone from a sealed key, no plaintext key on argv, sealed at rest, migration, record fingerprints, trust with an operator override, never print a key, warn when the pki key will not persist, expiry and renewal, say why trust failed), the non-goals, seven acceptance tests done by hand, and three open questions.
author: an agent working with Dinis Cruz on pki.sgit.ai, shared by him on 24 October 2026
status: published
---

# Sealed vault keys in sgit: requirements

**Draft for the sgit team.** Written 24 October 2026 against `sgit-ai` v0.24.0 and the `pki-agent` tool
published at pki.sgit.ai. The leak points and behaviours below were checked on that version; the
requirements come from a fortnight of moving vault keys between a person and many agent sessions, by
paste and then by sealed QR code.

---

## The goal in one line

A vault key should travel sealed to its recipient's public key, open only in memory, and be stored
at rest still sealed, so that **no vault key is ever written in cleartext to a transcript, a command
line, a temp file or a working copy**.

## Why: where a vault key is in cleartext today

Sealed delivery through `pki.sgit.ai` already fixes the worst problem, the chat transcript. Three
places remain, all checked on v0.24.0:

| # | Where | How it happens | Lifetime |
|---|---|---|---|
| 1 | `.sg_vault/local/vault_key` in every clone | `sgit clone <key>` writes the key there in plaintext (mode 0600) | as long as the clone exists, on every machine that ever cloned |
| 2 | process arguments and shell history | the key is a positional argument to `sgit clone`, and `pki-agent seal --text` takes it on the command line | process lifetime; shell history indefinitely |
| 3 | the output of `pki-agent open --save DIR` | the opened secret is written to a file so that sgit can use it | until someone shreds it |

Point 1 is the one that matters. A sealed handover that ends in `sgit clone <key>` has protected the
key in transit and then written it to disk in the clear. Every working copy on every agent's machine
holds every vault key that agent has ever opened.

## What is already in place

The parts needed are built. This is wiring, not new cryptography.

- `sgit pki encrypt` / `sgit pki decrypt`: hybrid RSA-OAEP-4096 and AES-256-GCM, keys in
  `~/.sg-send/keys`.
- `pki-agent` (pki.sgit.ai): identities, a register, a pinned root, `seal` and `open`, and QR codes
  as strict JSON. Its `seal --from-vault` already reads the key from `sgit vault show-key` into
  memory without printing it. That is the pattern to generalise.
- The sealed message format (`m1.…`) and the key code (`k1.…`, which carries both public keys and
  the label).

## Requirements

### R1. Clone and attach from a sealed key

`sgit clone` and `sgit vault attach` accept a sealed key in place of a plaintext one:

```
sgit clone --sealed handover.png   <dir>
sgit clone --sealed m1.…           <dir>
sgit clone --sealed handover.enc   <dir>
sgit clone --sealed -              <dir>    # read the sealed form from stdin
```

The key is decrypted in memory with the local pki key and never written in cleartext.

### R2. Never take a plaintext key on argv by default

A plaintext key passed as a positional argument should either be refused with a pointer to
`--sealed` or stdin, or accepted with a warning that names the exposure (process list and shell
history). Keep an explicit opt-in for scripts.

### R3. Keep the key sealed at rest

Instead of `vault_key` in plaintext, a clone stores the key **sealed to the local agent's own pki
key** (for example `.sg_vault/local/vault_key.sealed`). Every command that needs the key unwraps it
in memory and drops it afterwards.

What this buys: an agent no longer holds N vault keys in cleartext. It holds **one** secret, its pki
private key, which protects all of them. Retiring that pki key revokes the agent's access to every
vault it held, without rotating any of the vaults.

### R4. Migrate existing clones

`sgit vault seal-key` converts an existing clone's plaintext `vault_key` into the sealed form and
shreds the plaintext. Running it twice does nothing.

### R5. Address messages by the record fingerprint

A sealed message must be addressed to the recipient's **record fingerprint, which is the signing
key's**, not the encryption key's. `pki-agent open` refuses a message whose `to` does not match
(*"to or from does not match the sealed code: refused"*). We hit this building a sealer from the key
code, and it is easy to get wrong because the key code carries both fingerprints. The library should
offer one function that returns the right one.

### R6. Trust: chain to the pinned root, with an explicit operator override

By default, seal only to recipients that chain to the pinned root, as `pki-agent seal` does today.

Also support a **principal-vouched** mode, behind an explicit flag, for an operator who carries the
recipient's key QR by hand:

```
sgit pki seal --to-key-qr agent-key.png --vouched-by-operator ...
```

It takes the recipient bundle from the key QR instead of the register, skips only the register
check, and records that in the message itself (*"vouched by the operator in person, key carried by
hand"*), so the recipient sees how it was trusted. This is how two keys were handed to an agent that
was not yet enrolled, and it worked. It belongs in the tool, behind a named flag, rather than in a
patched copy.

When this mode is used, the operator is the only check that the key belongs to the agent. The flag's
help text should say so, and tell the operator to compare the QR's fingerprint with the one the agent
printed in its own session.

### R7. Never print a key, including in errors

No command prints a vault key, a read key or a sealed secret's contents, including in error messages
and `--debug` output. `pki-agent read-qr` already gets this right: it reports kind, recipient, sender
and size, and never the secret.

### R8. Warn when the pki key will not persist

If the pki key lives under a home directory that will not survive (a `--rm` container with nothing
mounted over `~/.sg-send`), say so at `keygen`. With R3 in place, losing the pki key loses access to
every vault sealed to it, so this becomes the single most expensive mistake an agent can make. We hit
it once: a keypair made in a `--rm` container printed a fingerprint and a success message, was gone
when the container exited, and the backup sealed to it could never be opened.

A cheap check: after `keygen`, look for the key again in a fresh process and fail if it is missing.
The store location is not configurable (`CLI__Main` calls `pki.setup()` with no argument, so it is
always `~/.sg-send`); `HOME` is the only lever. Adding a `--home` flag or an env var would help.

### R9. Expiry and renewal

A confirmed agent record has a validity window (seven days was observed). Add `sgit pki status`
showing the expiry, warn when it is under 48 hours away, and offer a renewal command. Without this,
enrolled agents stop being trusted without warning, and people go back to pasting keys.

### R10. Say why trust failed

"Not trusted" currently looks the same whether the agent was never enrolled, is enrolled but not
confirmed, has expired, or the register has not rebuilt yet. These need different responses. We
waited about a day for an operator's confirmation to appear in the register, with no way to tell
that from a failed confirmation. Report which of these it is, and when the register was last built.

## Non-goals: what this does not fix

- **The unattended secret.** An agent that runs without a person needs some secret it can use
  unattended: the pki private key, or the passphrase that protects it. R3 cuts the number of such
  secrets per agent to one. It does not get rid of it.
- **Forward secrecy.** The `expires` field on a sealed message is advisory, not cryptographic. If
  the recipient's private key leaks later, every message ever sealed to it can be opened.
- **Endpoint compromise.** Sealing protects the channel. A compromised agent session has the key
  once it opens it.

## Acceptance tests

Each of these was done by hand while writing this brief; they should be automated.

1. **Round trip through the stock tool.** Seal a throwaway vault's key with the new code path, open
   it with the unmodified `pki-agent open`, and compare the result byte for byte.
2. **No cleartext at rest.** After `sgit clone --sealed`, search the clone and the system temp
   directory for the key string. There should be no matches.
3. **No cleartext on argv.** While a sealed clone runs, the key does not appear in `ps` output or in
   shell history.
4. **Wrong recipient fails closed.** A message sealed to another agent is refused, and nothing is
   written.
5. **Tampering fails closed.** Flipping one byte of the ciphertext gives an authentication failure
   (`InvalidTag`), and nothing is written.
6. **Unverified sender is flagged, distinctly.** A message from a sender outside the register opens
   only with an explicit flag, and the report says *why* it is unverified.
7. **Pack-mode clones.** A sealed clone of a pack-mode vault works, and the scans in test 2 read
   through `sgit cat`, not the disk. In a sparse pack-mode clone the working tree is empty while
   `sgit ls` shows every file as present, so a disk scan would check nothing and report clean.

## Open questions

- Should a clone be able to hold its key sealed to **several** agent keys, so that two agents can
  share a clone without sharing a pki key?
- Should the register publish a revocation list that sgit checks before unwrapping a key at rest
  (R3), so that retiring a pki key takes effect straight away rather than when it is next used?
- Should the read key get the same sealed-at-rest treatment? It is less sensitive than the vault key,
  but it is still a credential, and pack mode makes "who can read this vault" matter more.

*Shared by Dinis Cruz on 24 October 2026 and published on cli.sgit.ai as written. Read against the design in [A vault key that never lands](/articles/a-vault-key-that-never-lands.html) in [Sealed vault keys: the requirements and the design, side by side](/research/sealed-vault-keys-side-by-side.html).*
