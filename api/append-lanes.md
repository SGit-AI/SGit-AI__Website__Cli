# Append lanes, cli.sgit.ai

> The six append endpoints) the write-only vault-to-vault message transport. Four separated capabilities, the blind write response, server-assigned sortable filenames, idempotent mark-processed, and the limits.

*Source: <https://cli.sgit.ai/api/append-lanes.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/api/append-lanes.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Append lanes

A write-only channel attached to a vault, gated by a token the writer holds and nothing else. This is the transport behind [vault-to-vault messaging](../docs/vault-messaging.md) and behind [`sg.append`](https://sgit.ai/docs/vault/sg-bridge.html) in the browser bridge, and it is deliberately generic: the same primitive carries messages, logs, signals, control messages and state flows.

**Naming.** This API was called **inbox** before v0.32.7. Every `/api/vault/inbox/*` URL is gone, and `purge` takes `folder:"pending"` or `"processed"`, the old `"inbox"` value returns **400**. If you are reading older material, translate.

**Checked in use, 26 September 2026.** Two agent teams ran two-way, signed messaging over these lanes on 25 and 26 September, and wrote down every place where this page differed from what the server did. [Their write-up](../docs/append-lane-messaging.md) is published on this site. The table below, and the sections marked *checked 26 September*, are corrected from it.

## The six endpoints

All **POST**, all under `/api/vault/append/`.

| Path | Gate | Does |
|---|---|---|
| `configure/{vault_id}` | `x-sgraph-vault-write-key`**and** the SG/Send access token (401 without it) | Registers `append_anchors`, hashes of accepted senders, and `enum_key_hash`. **It replaces the anchor list**: to add a sender, send every existing anchor plus the new one, or the existing lanes silently stop accepting writes |
| `write/{vault_id}` | `append_token`**in the body** | Appends a payload. **Account-less**: no access token required |
| `list/{vault_id}` | `x-sgraph-vault-enum-key` | Paginated listing, optionally with inline content. Each entry's `inbox` is the lane's **raw token** (see below) |
| `fetch/{vault_id}` | enum key | Body `{"inbox": <token>, "file_ids": [...]}`: the lane must be named. **Pending files only**: once a file is marked processed it cannot be fetched again, so keep the ciphertext if you may need to re-verify it |
| `mark-processed/{vault_id}` | enum key | Body `{"inbox": <token>, "file_ids": [...]}`. Moves pending → processed. Idempotent |
| `purge/{vault_id}` | `x-sgraph-vault-write-key` and the SG/Send access token (401 without it; checked 29 September) | Body `{"inbox": <token>, "folder": "pending" | "processed"}`. Deletes |

## Where the routes are, and what a failure looks like checked 26 September

- **The routes are on `https://dev.send.sgraph.ai` only.** `send.sgraph.ai` has no append routes today.
- **A bad key or an unknown token returns 404 with an HTML page**, not a 403 with JSON. A missing field returns a JSON 400. When a call 404s, check the key before the path.
- **Getting the write key.** It is derived from the vault key: `Vault__Crypto().derive_keys_from_vault_key(vault_key)['write_key']`. The parser strips the `sgit_private_vault_` prefix first; deriving from the raw string gives a different key, and every call 404s.

## The payload, exactly checked 26 September

`sgit pki encrypt` writes the `.enc` file as base64 text of a JSON envelope. The `payload` sent to `write` is base64 of that file's bytes, so the envelope is **encoded twice**:

```
payload  = base64(open("msg.eml.enc", "rb").read())        # sending
envelope = json.loads(b64decode(b64decode(content)))       # draining
```

A sender that encodes only once is rejected by a strict drainer. The recommendation to the sgit team is a single encoding, since the `.enc` text is already valid base64; until that changes, this is the format.

## Why the gates are split this way

Four capabilities, and the split is the whole design:

| Capability | Holder | Can | Cannot |
|---|---|---|---|
| `append_token` | the sender | write | list, fetch, read anything |
| `enum_key` | the vault owner | list, fetch, mark-processed | write, purge |
| `write_key` | the vault owner | configure, purge | none |
| private key | the vault owner | **decrypt** | *never sent to the server* |

A sender can put something into your vault and learn nothing at all, not the contents, not the volume, not whether anyone else writes there. The server stores `SHA-256` of the first three capabilities and compares hashes; the fourth it never sees.

## Four contracts worth relying on

- **The write response is blind.** `/write` returns exactly `{"ok": true}`, no file ID, no count, no metadata. This is a security property, not an oversight: a returned ID would leak lane state to a party who is only allowed to write.
- **Filenames are server-assigned** as `{epoch_ms:013d}_{24-hex}.enc`. Being chronologically sortable is what makes cursor pagination stable, pass the last file ID you saw as `after_file_id`.
- **Metadata-only listing is free.** `include_content: false` reads **zero** payloads. Poll with it, then fetch on demand; polling with content is the common way to hit the 3 MB ceiling for no reason.
- **mark-processed is idempotent.** An already-moved file comes back in `missing` rather than as an error, so retrying a batch after a timeout is safe.

## From a vault app: one verb crosses vaults, five do not

This is the constraint to understand before designing anything that spans two vaults, and it was undocumented until the SG/API team's review of 6 September 2026 (quoted here CC BY 4.0). The bridge builds **one** client bound to the **currently open vault**, with the enum key derived from that vault's read key. So:

| Verb | Which vault it acts on | Bridge permission |
|---|---|---|
| `write` | **Any**: it takes an explicit `vault_id` and posts with no headers at all | `append.write` |
| `list` | Always the open vault. There is no way to address a remote vault with these from an app | `append.list` |
| `fetch` | `append.read`, **not**`append.fetch` |
| `markProcessed` | `append.markProcessed` |
| `purge` | `append.purge` |
| `configure` | `append.configure` |

All six are plain booleans, **default-deny**, not path-scoped. The asymmetry is deliberate rather than a gap: listing a remote lane needs the recipient's enum key, and shipping that inside a published app *"would give every visitor read access to the whole lane."*

**Two things that are *not* gates on `append`, despite appearances.** There is **no read-only check** anywhere in the append handler, `sg.app.writable` is irrelevant to it, and a read-key session can write to a lane given the grant. And the CSP is not an append rule: the frame ships `connect-src blob: data:`, so a *direct* `fetch` to these endpoints is blocked unless the app declares `permissions.network: true`, which reopens all egress and is the worse choice. Use the bridge. See [the build brief](https://sgit.ai/docs/briefs/vault-telemetry-append-lanes.html), which had both of these wrong until the review corrected it.

## The `inbox` field is the lane id, and today it is the token

A `list` response labels each entry with an `inbox` value. That value is the storage folder name, and the folder is named by the **raw append token**, byte for byte, while `config.append_anchors` stores `sha256(token)`. So the design hashes the token in config and then writes the plaintext token into the object key.

The disclosure is bounded: `list` is gated by the enum key, so it reaches only the vault owner, who already holds every credential in play; and the token is a **write-only lane address**, closer to an email address than a password. The residual risk is storage rather than API, the raw token becomes an object key, so it lands in access logs, inventory reports and backups, *"surfaces with a very different audience from the enum-key holder."* The team intends to fold the folder name to `sha256(token)`, which is a breaking change needing a migration. **Documented here now so that nobody has to discover it from a debrief.**

Lanes live at `bare/append/{token}/pending/` and `…/processed/`, **outside the version-controlled commit tree**: appends never touch a branch and never conflict with a push.

## Several senders on one vault

Register several `append_anchors` and each sender writes into their own lane, distinguished by their token. A listing can be scoped to one lane, so one correspondent flooding you does not bury another, and revoking one sender is removing one anchor, with no effect on the rest.

## Limits and codes

| Limit | Value | On breach |
|---|---|---|
| Payload per write | 5 MB | 413 |
| Pending files per token | 1000 | 507 |
| File IDs per batch | 100 | 400 |
| Inline content when listing | 3 MB cumulative | 413 |
| Page size | 50 default, 200 max | clamped silently |

The `append_token` pattern is `^[0-9a-f]{16,128}$`, hex only. A prefixed token returns **400**, not 403; see [errors](../api/errors.md) for why that distinction saves time.

## See also

- [Vault messaging](../docs/vault-messaging.md), this API composed with PKI into a worked example
- [Append-lane messaging between agents](../docs/append-lane-messaging.md), the write-up of two-way use on 25 and 26 September: per-session keys, a pinned key registry, ephemeral inboxes, the threat model and the recommendations
- [`sg.append`](https://sgit.ai/docs/vault/sg-bridge.html), the same six operations from a vault app
- [Errors and limits](../api/errors.md)

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/api/append-lanes.html)*
