---
title: Vault objects
summary: The pointer store: read, write, batch, destroy and presigned endpoints, the caching contract that separates immutable content-addressed objects from mutable refs, and the storage layout behind every vault.
section: api
order: 3
moved_from: https://sgit.ai/api/vault-objects.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Vault objects

The pointer store: the ciphertext objects a vault is made of, addressed by opaque identifiers the server cannot interpret. This is what `sgit push` and `sgit pull` are doing underneath.

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| PUT | `/api/vault/write/{vault_id}/{file_id}` | access token + write key | Body is raw ciphertext |
| GET | `/api/vault/read/{vault_id}/{file_id}` | none | Raw bytes. [Reads are public by default](/api/authentication.html#reads) on the shared host |
| GET | `/api/vault/read-base64/{vault_id}/{file_id}` | none | Base64 in JSON, MCP-safe. Around 3.75 MB ceiling |
| DELETE | `/api/vault/delete/{vault_id}/{file_id}` | access token + write key |  |
| POST | `/api/vault/batch/{vault_id}` | per operation | Mixed reads and writes, **max 100** per request |
| POST | `/api/vault/list/{vault_id}` | none |  |
| GET | `/api/vault/health/{vault_id}` | none |  |
| GET | `/api/vault/public-info/{vault_id}` | none |  |
| DELETE | `/api/vault/destroy/{vault_id}` | write key | Body `{vault_id, purge?}`. Without `purge` it writes a tombstone that blocks reuse of the ID |

Large blobs go through presigned URLs rather than the request body: `POST /api/vault/presigned/initiate|complete|cancel/{vault_id}` and `GET /api/vault/presigned/read-url/{vault_id}/{file_id}`.

`GET /api/vault/zip/{vault_id}` is registered in the route table but marked PROPOSED upstream. It is deliberately [not documented](/api/index.html#unresolved) until that is reconciled.

## Destroy, and why the tombstone matters

`destroy` without `purge:true` leaves a tombstone that prevents the vault ID being registered again. That is a security property, not bookkeeping: vault IDs are short and a released ID is a squattable namespace. If somebody still holds a read key pointing at that ID, a new vault claiming it would be answering reads meant for the old one. `purge:true` skips the tombstone and frees the ID, use it only when you are sure no credential survives.

## The caching contract

Anyone writing a client needs this, and getting it wrong produces a bug that looks like corruption:

| Object | Response header |
|---|---|
| File ID containing `-imm-`, immutable, content-addressed | `Cache-Control: public, max-age=31536000, immutable` |
| Refs and indexes, mutable | `Cache-Control: no-store` |

Immutable objects are content-addressed, so their bytes can never change and a year-long cache is safe, which is what lets a vault sit behind a CDN. Mutable refs must never be cached: a stale ref renders a previous commit’s tree from ciphertext that is itself perfectly valid, so nothing errors and the reader simply sees the wrong version of the vault.

**Measured 21 September 2026: the immutable header is not currently being sent.** A GET of an `obj-cas-imm-` object on `/api/vault/read/` returned **no `Cache-Control` header at all**, and the CDN reported a miss. The table above is the contract, not a description of what is served on that path today. Build as though the header may be absent: cache on the id, which is a hash of the ciphertext and therefore cannot be stale, rather than on a header you were sent. That is what the client-side caches in this estate already do, and [why caching ciphertext is the easy case](https://sgit.ai/demos/fractal-graphs/performance.html#caching).

## Storage layout

```
bare/data/obj-cas-imm-{hex}     blobs, trees, commits — content-addressed, immutable
bare/keys/key-rnd-imm-{hex}     PKI public keys — immutable
bare/refs/                      branch refs — mutable
bare/indexes/                   branch index — mutable
bare/append/                    append lanes — managed, outside the commit DAG
```

The prefixes are load-bearing. `obj-cas-imm-` is SHA-256 over the *ciphertext*, which gives deduplication without the server knowing any plaintext, and makes the caching rule above derivable from the ID alone. Append lanes sit outside the commit DAG on purpose, a message arriving does not rewrite your history.

This site is itself served from a vault, so these are the objects behind the page you are reading. The [live-vault case study](https://sgit.ai/case-studies/live-vault-docs.html) shows the fetch sequence.

## See also

- [Append lanes](/api/append-lanes.html), the write-only channel that does not touch the commit tree
- [Errors and limits](/api/errors.html)
