# The transfer API, one encrypted handover, one link, cli.sgit.ai

> The other API family on this host: a single encrypted payload uploaded once and shared as one link. The two secrets that must not be confused, the SGMETA envelope that keeps the filename off the server, the three calls, revocation that is opt-in at create time only, and when a transfer beats a vault.

*Source: <https://cli.sgit.ai/api/transfers.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/api/transfers.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# The transfer API, one encrypted handover, one link

The other half of the API on this host. A **vault** is a versioned encrypted tree you clone, pull and push; a **transfer** is a single encrypted payload uploaded once and handed over as one link. Same server, same zero-knowledge property, different job, and until now this site documented a transfer *header* without documenting a single transfer *endpoint*.

**Provenance.** This page is derived from an integration guide written by the team that owns the SG/Send API, who executed **every request, response, status code and byte layout in it against the production user API on 9 September 2026**. That run is theirs, not ours. We have not re-executed it here, and the date is the one to check it against. Their guide is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Transfer or vault?

Pick this first; it decides everything after it.

|  | Transfer | [Vault](../api/vault-objects.md) |
|---|---|---|
| **Shape** | One payload, uploaded once | A versioned tree of files |
| **History** | None. There is no second version | Commits, branches, merges |
| **The reader gets** | The whole payload, or nothing | Any single file, without fetching the rest |
| **Lifecycle** | Expires, caps downloads, can be revoked | Lives until you delete it |
| **The credential** | A decryption key in the URL fragment | A [read key](https://sgit.ai/docs/vault/reading-a-vault-file.html), derived one-way |
| **Reach for it when** | An agent finishes a job and hands the result over **once**: a bundle, a report, a dated export | The thing is read repeatedly, browsed, updated, or rendered as an app |

The SG/API team's own guidance, for a workflow that ships one bundle per voice memo, is that the transfer API is *“the simpler and better fit”*. That is the right instinct in general: **a vault is the wrong answer for a handover that happens once.**

## Two secrets that must never be confused

This is the part that goes wrong first, and it goes wrong silently, a leaked access key does not throw.

|  | What it authorises | Where it goes |
|---|---|---|
| **The access key** `x-sgraph-access-token` | *You*, to upload | A request **header**. Never a URL, never a share link, never a log |
| **The decryption key** | *Anyone*, to read | The URL **fragment**: everything after `#`, which no browser sends to the server |

They are unrelated values. The fragment is what makes a share link both shareable and private: the key reaches the recipient's client and never the origin serving the page. The API also accepts `?access_token=` as a query fallback and it works, **do not use it**; query strings land in proxy logs, browser history and workflow execution records.

What the server can see: ciphertext size, a hashed sender IP, a creation timestamp, and the `content_type_hint` you supply. What it cannot see: the filename, the contents, or the key.

## The payload format, two layers, in this order

The filename must not reach the server, so it is wrapped *inside* the plaintext before encryption. Getting the order wrong produces a corrupt download with no name.

**Inner, the SGMETA envelope:**

```
"SGMETA\0"          7 bytes    53 47 4D 45 54 41 00
meta_len            4 bytes    uint32, big-endian
metadata JSON       meta_len   {"filename":"…"}  UTF-8
file bytes          rest       your payload
```

**Outer, AES-256-GCM over that whole buffer:**

```
IV                 12 bytes    random, fresh per upload, prepended
ciphertext + tag   rest        GCM appends its own 16-byte tag
```

- **Key:** 32 random bytes, shared as **base64url, unpadded**: 43 characters.
- **IV:** 12 random bytes, never reused with the same key.
- **Overhead:** the uploaded payload is exactly **28 bytes larger** than the plaintext (12 + 16).

Same primitive as everything else here: AES-256-GCM, done client-side, with the server holding ciphertext under a key it never had. [The security page](../security/index.md) covers why that is the whole product rather than a feature of it.

## The three calls

| Call | Endpoint | Notes |
|---|---|---|
| **1 · create** | `POST /api/transfers/create` | Returns `transfer_id`. Body carries `file_size_bytes` (the *plaintext* length, display metadata only), `content_type_hint` (stored in the clear, keep it generic), `max_downloads`, `auto_delete`, `expires_at` |
| **2 · upload** | `POST /api/transfers/upload/{id}` | **Raw bytes**: not base64, not multipart. `Content-Type: application/octet-stream` |
| **3 · complete** | `POST /api/transfers/complete/{id}` | Nothing is downloadable until this call lands |

Only those three need the access key. `info` and `download` are **public by design**: the decryption key is the gate, which is exactly why a share link works for someone with no account.

**Two traps in the create body.** `expires_at` is in **milliseconds** since epoch, not seconds; `0` means never. And `max_downloads: 0` means *unlimited*, not zero, once a finite allowance is exhausted, downloads return **410**.

### Build the share link yourself

`complete` returns a `download_url` of `/d/{id}`. **Ignore it**: verified as a 404; it is not a live route. The link to hand out is:

```
https://send.sgraph.ai/en-gb/download/#{transfer_id}/{key_base64url}
```

Omit `/{key}` for a link-only form when the key travels through a second channel. The fragment parser splits on the **first** `/` and truncates at a `|`, so `|` is reserved, base64url never produces one, so following the format above keeps you clear.

## What a receiving agent has to do

This is the payoff, and it is two calls with no account and no browser: `GET /api/transfers/download/{id}` needs no auth, and the key from the fragment does the rest, split the IV off the first 12 bytes, AES-GCM decrypt, check the `SGMETA\0` magic, read the big-endian length, and the filename and payload fall out. For a JSON-only transport such as an MCP tool, `GET /api/transfers/download-base64/{id}` returns the same bytes wrapped in JSON.

**Downloads are counted.** An agent retrying a failed run burns the allowance. For agent-facing links prefer `max_downloads: 0` with a short `expires_at`, time-bounded rather than attempt-bounded, because a retry is not a reader.

## Expiry, caps and revocation

Revocation is opt-in **at create time and only then**: set `delete_auth_hash` to `sha256(secret)` in hex and store the secret beside the transfer id. Without it, deletion is disabled for that transfer forever. To revoke, `DELETE /api/transfers/delete/{id}` carrying the access key and `x-sgraph-transfer-delete-auth: <the secret, not the hash>`, the one header [the authentication page](../api/authentication.md) already listed before this page existed to explain it.

**410 and 404 are both normal end states, not errors to retry:** 410 is gone-as-expected (expired or exhausted), 404 is never-existed-or-deleted.

## Size

| Path | Ceiling | When |
|---|---|---|
| **Direct upload** | keep the encrypted payload under **~4 MB** | The normal case |
| Multipart / presigned | Larger | Needs the S3 backend, check `GET /api/presigned/capabilities` first |

The ~4 MB figure is a working limit rather than a published one: the Lambda URL caps a request body at 6 MB and the browser client switches to presigned at 5 MB. Text bundles compress far below it; **audio does not**, and is usually the most sensitive part of a bundle as well as the largest.

## Verified behaviour

The SG/API team's run, 9 September 2026, reproduced here as they reported it:

| Case | Result |
|---|---|
| Header `x-sgraph-access-token` | **200** |
| Header `x-sgraph-send-access-token` | **401**: that name does not work |
| No token, or a wrong one | **401** |
| `download` / `info` with no token | **200**: public by design |
| Round trip: wrap → encrypt → create → upload → complete → download → decrypt → unwrap | **Byte-identical** payload recovered, filename intact |
| Download #3 against `max_downloads: 2` | **410** |
| Download of an expired transfer | **410** |
| `DELETE` with wrong / correct delete-auth | **403** / **200**, then **404** |
| `GET /d/{transfer_id}` | **404**: not a route |
| Key length | 32 bytes → 43 base64url characters |
| Encrypted payload overhead | plaintext + 28 bytes |

## The rules worth holding to

1. **Never log or return the decryption key** outside the share link. It is not an identifier, anyone holding it reads the payload. In a workflow engine that means keeping it out of node output that gets persisted.
2. **Never put the access key in a URL.** Header only.
3. **Never reuse an IV.** Twelve fresh random bytes per upload.
4. **Keep the filename inside the envelope.** `content_type_hint` is in the clear; the name is not, and that is the reason the envelope exists.
5. **Always set an expiry.** A link pasted into a chat lives as long as the chat does; the transfer should not.
6. **Bundle for a reader who is an agent**: a `manifest.json` saying what each file is, and an `llms.txt`, cost nothing and are the difference between a payload that can be used and one that has to be opened by a person first.

Adapted with attribution from the SG/API team's integration guide of 9 September 2026 (CC BY 4.0); the workflow-specific half of that document (credential wiring, node shapes, the bundle layout for one product) stays with the product it was written for. [API reference](../api/index.md) · [Vault objects](../api/vault-objects.md) · [Append lanes](../api/append-lanes.md) · [Working on a vault](https://sgit.ai/docs/guidance/index.html)

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/api/transfers.html)*
