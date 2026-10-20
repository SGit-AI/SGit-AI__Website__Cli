---
title: Vault key management: where each key lives, and how it travels
summary: The reference for sgit-ai v0.20.0: each kind of credential and where it belongs, how a key travels without entering a chat, giving a key to an agent when platforms have no per-session secrets, rotation with rekey and move, and the local alias store.
section: security
order: 2
moved_from: https://sgit.ai/docs/key-management.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Vault key management: where each key lives, and how it travels

A vault is encrypted in the client, so the server never holds a key and the key is the whole question: whoever holds it holds the vault. This page is the reference for sgit-ai v0.20.0: each kind of credential, where it should be kept, how a key travels without entering a chat, how to give one to an agent, and how to rotate one. The reasoning and the roadmap are in the article [Where the vault keys live](https://sgit.ai/articles/where-the-vault-keys-live.html).

**Why this page exists, with the date on it.** On 10 October 2026 a reader asked where the keys of the vaults that temporary agent sessions write to are managed. The docs explained what each credential can do ([vault credentials](/docs/credentials.html)) and how to hand a key to a registry ([send a vault key](/docs/send-a-vault-key.html)), but nowhere said where keys should live. This page is that answer.

## Each credential, and where it belongs

| Credential | Can | Keep it in | Publish? |
|---|---|---|---|
| **Vault key** `sgit_private_vault_<passphrase>:<vault_id>` | Read and write the vault, and derive everything below | A password manager, for keys a person holds. A registry vault, for keys agents create. The working session that needs it, for as long as it needs it | **Never.** Not in a page, a repository, a commit message, an issue, a log or a chat |
| **Read key** `sgit_public_read_<read key>:<vault_id>` | Read every file and every commit | Anywhere you would put the content itself | Yes, on purpose, under the public prefix. Check it with `check_credential.py` first |
| **Write key** | Push, and configure append lanes with the access token | Derived when needed (`sgit vault derive-keys`); nowhere on its own | Never |
| **Append token** | Write to one lane, blind | The one sender it was issued to, one token per sender | Never. Retire it once it has appeared anywhere durable |
| **Enumeration key** | List, fetch and mark lane messages processed | The vault owner, beside the vault key | Never |
| **PKI private key** | Decrypt what was sealed to you; sign | The machine or vault that generated it (`sgit pki keygen`) | Never. Publish the public bundle (`sgit pki export`) instead |
| **SG/Send access token** | Use a server: create, push, configure | The environment of the sessions that push, as narrowly as the platform allows (see below) | Never |

## How a key travels

- **Into the registry.** The agent that made the vault seals the key to the registry's public key and writes it to the registry's append lane with a write-only token. It never displays the key. The full instructions, for the agent that has to follow them, are on [send a vault key](/docs/send-a-vault-key.html).
- **To a person.** Through their own password manager, or a lane of their own sealed to their public key. Not in a message thread: a transcript is a durable record held by someone else.
- **Onto a page.** As a read key only, with the `sgit_public_read_` prefix, after `check_credential.py` classifies it. The build refuses any `sgit_private_` credential in a tracked file.
- **To another agent.** See the next section. Where you can, let the agent create its own vault and send the key back on a lane, so no key has to be handed in.

## Giving a key to an agent

An agent needs three things to work with a vault: the key, sgit, and network access to the API host (or a server in its own network: [self-hosting](/docs/self-host-for-agents.html)). The key is the hard part, because agent platforms do not have secrets per session.

- **Claude Code on the web.** Environment variables belong to the environment and "any command Claude runs can read" them; on Team and Enterprise, every member's sessions in a shared environment read its variables ([cloud environments](https://code.claude.com/docs/en/cloud-environments#set-environment-variables)). On Pro and Max, a **network secret** is attached by the agent proxy outside the session, which suits a server token such as the SG/Send access token, but not a vault key, which has to be inside the session to decrypt.
- **OpenAI Codex cloud.** Secrets reach setup scripts only and are removed before the agent runs ([cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environment)).
- **What we do meanwhile.** One small vault per conversation or job, so each key opens little; the agent creates the vault where it can, and sends the key to the registry; a key that had to be pasted into a prompt is treated as exposed, and the vault is rotated when the work ends.

## Rotation and retirement

- `sgit vault rekey` replaces the vault key and re-encrypts all content (`check`, then `wipe`, `init`, `commit`).
- `sgit vault move` moves the vault to a new identity, a new key and optionally a new server, in eight steps with `--dry-run` and `--cleanup`.
- **Rotation is not retroactive.** Anyone who already fetched the objects keeps them; a new key protects future commits only. Treat a leaked read key as published content, and a leaked vault key as a reason to rotate now.
- **Retire lanes** whose tokens have appeared anywhere durable: reconfigure the lane without that anchor.

## On one machine

`sgit vault add <alias>`, `sgit vault list`, `sgit vault show <alias>` and `sgit vault remove <alias>` keep keys under aliases on one machine. That is convenient on a laptop. It is not a backup: an ephemeral container loses it with everything else when it is reclaimed, so a key that matters is also in the registry or a password manager.

## What comes next

Integrations with password managers ([the open call](https://sgit.ai/partnerships/vault-key-management.html)), the passkey-unlocked keyring of [secrets.sgit.ai](https://secrets.sgit.ai/), [PKI](/docs/pki.html) for sharing without shared secrets, and decryption that happens out of band. Statuses are in [the article](https://sgit.ai/articles/where-the-vault-keys-live.html#next).

Checked against sgit-ai v0.20.0 and the live API documentation of `send.sgraph.ai` (v0.32.4) and `dev.send.sgraph.ai` (v0.33.69) on 10 October 2026.
