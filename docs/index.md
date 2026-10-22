# Docs, cli.sgit.ai

> Every page of the sgit CLI documentation in reading order: getting started, the guides, and the security pages, with the command reference and the HTTP API alongside.

*Source: <https://cli.sgit.ai/docs/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# The sgit CLI documentation

Read the first section in order; the rest when you need it. Commands are in [the reference](../reference/index.md), generated from the CLI itself; the protocol underneath is in [the HTTP API](../api/index.md). Most of these pages were written for sgit.ai and [moved here](../admin/moved.md) on 20 October 2026; each one says where it came from.

## Get started {#start}

- [What is sgit](../docs/what-is-sgit.md): sgit is git for encrypted vaults: how it works, what makes it different from git, and the ecosystem around it.
- [Installation](../docs/installation.md): Install sgit with pip, verify with sgit doctor, upgrade with sgit update. Python 3.11+, two runtime dependencies.
- [Quickstart](../docs/quickstart.md): From zero to a synced, encrypted, versioned vault in five minutes: create, commit, push, clone, pull.
- [sgit for git users](../docs/sgit-for-git-users.md): The Rosetta stone: every git command mapped to its sgit equivalent, plus the three deliberate differences.
- [The two-branch model](../docs/two-branch-model.md): sgit's central idea: private clone branches per machine or agent, shared named branches, and explicit publishing.
- [When NOT to use sgit](../docs/limitations.md): The honest page: sgit's edges, stated plainly, plus the current roadmap gaps.

## Guides {#guides}

- [Partial clones: a folder scope and a history depth](../docs/partial-clones.md): sgit clone --path holds one folder and carries the rest by id; --depth holds the newest commits only. Measured on a 600-commit vault: one folder in 14 s against 80 s for the whole vault. The rules, widening with sgit fetch, the commands that need a full clone, and the two edges.
- [Pack mode: a playbook for agents](../docs/pack-mode-for-agents.md): Everything an agent needs to use sgit pack vaults (sgit-ai 0.24.0 and later) in a project, as recipes to follow in order. Decide whether a vault should be a pack vault; create one, or convert a copy of an existing vault and cut a team over to it; the daily loop and what its output should look like; who compacts, when, and how; the patterns for CI jobs, many agents, read-only readers and throwaway vaults; the health checks; every error message an agent will meet, with what to do; what never to do; and a block to paste into an agent's own instructions.
- [History integrity: the format gate, verifying signatures, and rewinds](../docs/history-integrity.md): sgit vault format (format 2, 128-bit ids, --min-client), who can open a raised vault and what old clients say, the shared branch index, rewind detection and --accept-rewind, sgit check verify, signatures-required and what a signature proves, and a checklist for raising a vault. For sgit-ai 0.21.0.
- [Working with AI agents](../docs/agents.md): The agent-facing surface: sgit write, --json everywhere, the clone modes including scoped and shallow clones, the session pattern, and multi-agent collaboration.
- [Agents sharing one vault](../docs/agents-sharing-one-vault.md): The loop for a team of agents on one vault with sgit-ai 0.18.0: a scoped shallow clone per session, status before commit, push that pulls first, and the full table of what a pull does with uncommitted work: kept when untouched, refused by name when it would be overwritten.
- [Sending messages between vaults](../docs/vault-messaging.md): How two vaults exchange encrypted messages without sharing a vault key and without the sender holding an account: append lanes addressed by a token, composed with PKI. Worked example in CLI, curl and sg.append, with the one step that is not yet wired marked PROPOSED.
- [Append-lane messaging between agents that hold no one else's vault key](../docs/append-lane-messaging.md): The write-up of two-way, signed and encrypted messaging between agents over sgit's append lanes, as two teams ran it on 25 and 26 September 2026: per-session signing keys with a pinned key registry on the sender's own site, ephemeral inbox vaults for agents that keep no secret, the flows, security properties, threat model, HTTP calls as observed, eleven places sgit.ai's docs differed, and recommendations for sgit. Relayed by sgit.newsroom.sgit.ai.
- [Self-hosting a vault server for agents](../docs/self-host-for-agents.md): Encrypted memory for agents in VMs, containers, a Mac mini or ephemeral jobs: run the SG/Send container with an access token and a storage folder, create the vault, the agent's clone-work-push entry point, Docker Compose, Kubernetes manifests, the cloud, a second server, what the server holds, and the errors you may meet (--endpoint, mcp<2, port 8080).
- [Send a vault key to the registry](../docs/send-a-vault-key.md): For an agent that holds SG/Send vault keys and was given this page, an inbox vault id and an append token: the rules (never display a key, never improvise a route), the vault-key-handover/v1 payload, the registry's public key and endpoint, a sender script that pins the key's fingerprint, what to do afterwards and on a 404. The id and the token are never published.
- [Using sgit from Claude on a Team or Enterprise plan: the network allowlist](../docs/how-to/claude-team-egress.md): On Claude Team and Enterprise plans an Owner sets the code sandbox's network access for the whole organisation, and the default blocks every sgit host. Which domains to allow (apex domains explicitly), how to check from inside a session, how a proxy's CONNECT 403 differs from a server outage, and why web fetch can read sgit.ai while the shell cannot.
- [sgit-ai 0.24.0 release notes: pack mode](../docs/update-to-0-24-0.md): Release notes for sgit-ai 0.24.0, for people and agents. Pack mode is new and opt-in: a vault whose objects travel as zips, cloned in a handful of requests whatever its history, with files compressed before they are encrypted. The commands (init --packs, pack import, export, compact, ls, stats, verify), what was measured, the gate that refuses older clients by name, what does not work on a pack vault yet, the two transport changes every vault gets, and how the release was reviewed. Normal vaults behave as before.
- [Update sgit-ai to 0.21.0](../docs/update-to-0-21-0.md): For an agent team: sgit update, what now refuses and what to do (symlinks, unreadable files, SGIT_DEFAULT_BASE_URL, key zips, branch names, rewinds, signatures), the new history commands (undo, reflog, amend, revert --as-commit, shorthand, log filters), signed tags, --force-with-lease, notes for vault owners and mixed 0.20/0.21 teams. Covers 0.19.0 and 0.20.0. Published 11 October 2026.
- [Update sgit-ai to 0.18.0](../docs/update-to-0-18-0.md): Five minutes for an agent team: sgit update, check the version, change the clone command to --path and --depth, and what to do when a pull is refused. Published 7 October 2026.

## Security {#security}

- [Security model](../security/index.md): sgit's zero-knowledge security model, precisely stated: the crypto stack, what the server can and cannot see, key strength, and the open security process.
- [Vault key management: where each key lives, and how it travels](../docs/key-management.md): The reference for sgit-ai v0.20.0: each kind of credential and where it belongs, how a key travels without entering a chat, giving a key to an agent when platforms have no per-session secrets, rotation with rekey and move, and the local alias store.
- [Vault credentials: what each one can do, and what its prefix declares](../docs/credentials.md): Two capabilities, a vault key that reads and writes and a read key derived from it one way, plus the five prefixes that declare which you are holding and whether it was meant to be published. Why sgit_public_read_ is the form for an open vault, why publishing one under sgit_private_read_ is a mislabel that an agent will correctly refuse, and why the word matters when the bytes are identical.
- [Keys, signatures and encrypting to someone else](../docs/pki.md): The keypair lifecycle run end to end on the shipped CLI: RSA-OAEP 4096 encryption, ECDSA P-256 signing, the JSON public-key bundle, the hybrid envelope format, and what PKI does not do yet.

## Elsewhere

- **[Command reference](../reference/index.md)**: all 165 commands of sgit-ai v0.24.0.
- **[HTTP API](../api/index.md)**: the surface the CLI is a client of.
- **[Research](../articles/index.md)**: why the CLI is shaped the way it is, measured.
- **Vaults as a platform** (vault apps, `_page.json`, the browser bridge, publishing a vault) stay on sgit.ai: [Working on a vault: start here](https://sgit.ai/docs/guidance/index.html).

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/index.html)*
