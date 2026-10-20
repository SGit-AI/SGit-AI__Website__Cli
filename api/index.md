# The HTTP API, cli.sgit.ai

> The protocol surface behind sgit: base URL, the capability model, and the reference for vault objects, append lanes, authentication headers and error codes. Built from a code-verified audit at v0.33.54, with unresolved endpoints labelled rather than guessed at.

*Source: <https://cli.sgit.ai/api/index.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/api/index.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# The HTTP API

Everything sgit does, it does over this API. The CLI is a client; so is the browser bridge; so is anything you write. This section is the protocol surface, endpoints, headers, gates, limits and the error codes you will actually hit. **Two families share this host**: [vaults](../api/vault-objects.md), which are versioned trees you clone and push, and [transfers](../api/transfers.md), which are single encrypted handovers.

**Where this came from, and how far to trust it.** This section is built from a code-verified audit supplied by the SG/API team, read out of the route tables and constants at **v0.33.54** rather than recalled. It is *their* verification, not ours: this site has not independently exercised every endpoint. Where their audit and the shipped client disagreed we checked and said so; where something is registered but unconfirmed it is labelled **PROPOSED** and you should not build on it yet. Same rule as the rest of this site, if it is not verified, it says so.

## Base URL

`https://send.sgraph.ai` for the hosted service, or your own host if you [run it yourself](https://sgit.ai/deploy/index.html). All request and response bodies are JSON unless stated otherwise.

## The one idea worth reading first

The server is a **capability-checked ciphertext store**, and every access-control decision it makes is a hash comparison. It stores `SHA-256` of each capability key and checks `H(presented) == stored`. It never holds a raw key, and it never holds a private key at all.

That is what makes the rest of the design possible: a vault ID is an address rather than an account, reads are public by default because the bytes are useless without a key, and a stranger can write to your vault without ever having a credential on the platform.

## The reference

| Page | What is in it |
|---|---|
| [Authentication](../api/authentication.md) | The six headers, what each gates, and the hash-comparison model |
| [Vault objects](../api/vault-objects.md) | The pointer store (read, write, batch, destroy) plus the caching contract and storage layout |
| [Append lanes](../api/append-lanes.md) | The six append endpoints: the vault-to-vault message transport |
| [Transfers](../api/transfers.md) | The other family on this host: one encrypted payload, uploaded once, handed over as a single link, the SGMETA envelope, the three calls, and when to reach for this instead of a vault |
| [Errors and limits](../api/errors.md) | 400, 403, 413, 507, what each actually means, and the ceilings that produce them |

## Four capabilities

Most of the API surface is one of four capability tiers. They are separated so that holding one tells you nothing about the others:

| Capability | Presented as | Grants |
|---|---|---|
| `append_token` | a field in the request body | Write to one append lane. Nothing else, not even listing it |
| `enum_key` | `x-sgraph-vault-enum-key` | List, fetch and mark-processed on append lanes |
| `write_key` | `x-sgraph-vault-write-key` | Write and delete objects; configure and purge lanes |
| private key | *never presented* | Decryption, client-side only |

The fourth row is the point of the design rather than a footnote: the server cannot decrypt anything it stores, so the strongest capability in the system is the one it never sees.

## Where to start

- Sending an encrypted message between two vaults → [Vault messaging](../docs/vault-messaging.md), which composes [append lanes](../api/append-lanes.md) with [PKI](../docs/pki.md).
- Reading or writing files → [Vault objects](../api/vault-objects.md).
- Building a vault app in the browser → the [SG bridge](https://sgit.ai/docs/vault/sg-bridge.html) wraps this API so you never write HTTP.
- Using the CLI instead → [Quickstart](../docs/quickstart.md).

## Open questions we will not guess at

Three items came through the audit unresolved. They are listed rather than documented, because a confident page about an endpoint that does not exist is worse than no page:

| Item | Status |
|---|---|
| `GET /api/vault/zip/{vault_id}` | **UNRESOLVED**: registered in the route table, marked PROPOSED in the team’s reality document. Not documented either way until that is reconciled |
| `/join/*` | **UNRESOLVED**: the reality document lists three live endpoints, but the routes are not registered in the deployed app. Not documented |
| Client-side lane addressing | **PROPOSED**: `append_token = H(public key)` is the intended model; no shipped command emits it. See the [addressing note](../docs/vault-messaging.md#addressing) for what to do meanwhile |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/api/index.html)*
