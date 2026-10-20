# Authentication, cli.sgit.ai

> The six authentication headers, what each one gates, and the hash-comparison model: the server stores SHA-256 of every capability key and never holds a raw key or a private key. Includes why vault reads are open by default.

*Source: <https://cli.sgit.ai/api/authentication.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/api/authentication.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Authentication

Six headers exist. Which apply depends on the endpoint and on how the server is deployed. None of them is a password, and none of them is stored: the server keeps `SHA-256` hashes and compares.

## The headers

| Header | What it gates |
|---|---|
| `x-sgraph-access-token` | The SGraph account or deployment. In a **single-key self-hosted deployment** this gates *every* route, including reads |
| `x-sgraph-vault-write-key` | Vault write capability: writes, deletes, destroy, and append `configure` / `purge` |
| `x-sgraph-vault-enum-key` | Append lane enumeration: `list`, `fetch`, `mark-processed` |
| `x-vault-read-key` | Read key, for public-vault routing |
| `x-vault-public` | Public-vault routing flag |
| `x-sgraph-transfer-delete-auth` | [Transfer deletion](../api/transfers.md), SG/Send transfers, not vaults. Carries the *secret*, never the hash, and only works if a `delete_auth_hash` was set at create time |

One capability is **not** a header: `append_token` travels in the request body of `/append/write`. That is deliberate, see [append lanes](../api/append-lanes.md).

## The hash-comparison model

The server never stores a capability key. It stores `SHA-256(key)` and, on each request, hashes what you presented and compares. Two consequences worth designing around:

- **A server compromise yields hashes and ciphertext**, not keys and not plaintext. An attacker with the whole database still cannot read a vault.
- **There is no recovery path.** The server cannot email you your key, because it has never had it. Same property as the vault key itself, for the same reason.

## Why reads are open by default

`GET /api/vault/read/{vault_id}/{file_id}` requires no authentication on the shared host, which surprises people. It follows from the encryption model rather than being a gap in it: the bytes are AES-256-GCM ciphertext under a key the server has never seen, and the file IDs are HMAC-derived opaque identifiers that reveal no filename. Serving them to an anonymous caller discloses nothing a reader could use.

It is also the property that makes a [published read key](https://sgit.ai/demos/vaults/index.html) work at all, and what lets vault content sit behind an ordinary CDN. If that trade is wrong for your deployment, run in single-key mode, where the access token gates reads too.

What an unauthenticated reader *can* learn is covered honestly on the [security page](../security/index.md#server-sees): object sizes, timing, and approximate activity volume.

## See also

- [Errors](../api/errors.md), what a 403 means as against a 400
- [Security model](../security/index.md), the crypto these capabilities sit on

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/api/authentication.html)*
