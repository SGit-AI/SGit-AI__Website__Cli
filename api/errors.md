# Errors and limits, cli.sgit.ai

> 400, 403, 413 and 507: what each means, why a malformed token returns 400 rather than 403, the input patterns enforced before storage is reached, and every documented ceiling.

*Source: <https://cli.sgit.ai/api/errors.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/api/errors.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Errors and limits

Four status codes carry almost all the failures, and telling them apart saves real debugging time, particularly 400 versus 403, which fail for opposite reasons.

## Status codes

| Code | Means | What to do |
|---|---|---|
| **400** | Invalid input, the value never reached a gate. Malformed token, malformed file ID, batch too large, unknown `folder` value | Fix the *shape* of what you sent. Your credential may be perfectly valid |
| **403** | Gate failure, well-formed input, wrong capability | Fix the *credential*. The request shape was fine |
| **413** | Too large, payload over 5 MB, or an inline-content listing over the 3 MB ceiling | Split the payload, or list without inline content and fetch on demand |
| **507** | Lane full, 1000 pending files for that token | Fetch and `mark-processed`, then `purge` the processed folder |

**The 400 that looks like a 403.** Path and token components are validated by typed primitives *before* they reach storage, which is how path traversal is blocked at the type level. A prefixed token such as `tok_abc…` (or a CLI fingerprint pasted straight in, `sha256:a461…`) fails the hex-only pattern and returns **400**. It reads like a rejected credential; it is a rejected string. Use raw hex.

## Input patterns

| Input | Pattern |
|---|---|
| `append_token` | `^[0-9a-f]{16,128}$`: hex only, no prefix |
| `file_id` (append) | `^\d{13}_[0-9a-f]{24}\.enc$`) server-assigned, so you should be echoing one back |
| `vault_id` | lowercase alphanumeric, 8–24 characters, no hyphens |

## Limits

| Limit | Value | On breach |
|---|---|---|
| Payload per append write | 5 MB | 413 |
| Pending files per append token | 1000 | 507 |
| File IDs per batch (fetch / mark / purge) | 100 | 400 |
| Operations per `/vault/batch` request | 100 | 400 |
| Inline content when listing | 3 MB cumulative | 413 |
| Append list page size | 50 default, 200 max | clamped silently |
| `read-base64` response | ~3.75 MB | use [presigned reads](../api/vault-objects.md) above this |

The page-size clamp is silent: ask for 500 and you get 200 with no warning. Page with `after_file_id` rather than assuming your requested size was honoured.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/api/errors.html)*
