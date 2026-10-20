# Send a vault key to the registry, cli.sgit.ai

> For an agent that holds SG/Send vault keys and was given this page, an inbox vault id and an append token: the rules (never display a key, never improvise a route), the vault-key-handover/v1 payload, the registry's public key and endpoint, a sender script that pins the key's fingerprint, what to do afterwards and on a 404. The id and the token are never published.

*Source: <https://cli.sgit.ai/docs/send-a-vault-key.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/send-a-vault-key.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Send a vault key to the registry

You are an agent holding one or more SG/Send vault keys, and you were given this page's URL, an **inbox vault id** and an **append token**. This page is everything else you need. Follow it, and stop.

**What this is.** A private vault, the registry, holds the keys to the other vaults in this estate, so that a key is never lost and never lives in a browser tab or a chat. Keys reach it sealed to its public key, on a write-only append lane. The two values you were given are the only things not on this page: together they authorise a write, so they are handed out one sender at a time and never published. Everything on this page is public on purpose.

## Rules, before anything else

- **Never display a vault key.** Not in your reply, not in a summary, not partially, not in a file you keep, not in a commit message, not in a log. A chat transcript is a durable record, and this channel exists so that a key never enters one.
- **Never improvise another delivery route.** If this does not work, report the status code and stop. Do not offer to paste the key, email it, or put it anywhere else.
- **Keep the vault id and the token out of anything you publish.** Either one alone is useless; together they are a write credential for your lane.
- **Your token is write-only.** It cannot list, read or delete anything, not even what you just wrote. You cannot check your own send by reading the lane, and that is intentional.

## What to send

A `vault-key-handover/v1` payload. Only `vault_key` is required; the other fields make the registry's entry useful. Put every key you hold in one payload.

```
{
  "schema": "vault-key-handover/v1",
  "handover_id": "2026-10-07-your-name-01",
  "from": "agent@your-site.example",
  "vaults": [
    {
      "vault_key": "sgit_private_vault_<passphrase>:<vault_id>",
      "title": "short name for the vault",
      "slug": "short-slug",
      "one_line": "what it is and why it matters",
      "sensitivity": "what care it needs",
      "publication": "NOT PUBLISHED",
      "tags": ["website"],
      "notes": "anything the registry should record"
    }
  ]
}
```

Send `vault_key` exactly as sgit gave it to you, prefix and all. A **read key** is accepted too and recorded as read-only; where the registry only needs to read a vault, hand over the read key rather than the vault key. `handover_id` must be unique: a repeat is dropped as a replay. Everything you write in the text fields is stored as **unverified sender claims**, kept apart from the registry's own fields, so make it useful rather than persuasive.

## Where it goes

| Value | Where it comes from |
|---|---|
| Inbox vault id | **given to you**, with your token. Deliberately not on this page |
| Append token | **given to you**. Deliberately not on this page |
| Endpoint | `https://dev.send.sgraph.ai`, the only host with the append routes |
| Public key to seal to | `sha256:20b7bb9dbac7df90`, RSA-OAEP 4096, below and inside the script. Recompute the fingerprint from the PEM (SHA-256 of the SubjectPublicKeyInfo DER, first 16 hex characters) before you seal anything |

```
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAt2j3zEqSeQnXjJWIhcyk
OslbIjYqvIKRy1seGB2J9QR6o/xaDI6nY7ZtDBOya/nEobSQmjP+qoeTDjfK3jRa
oNIG90qMsFuk+9MotSCfnU7USeJBtKWUoL9IT9xXwFsHRKym5VhPxPDP3ptsNbYZ
ngab1eOQcKzyC8LRGPamJrz4LeuLv9nbEBP6Njt4c3WF8xap3DidW2W2pzhpUl/i
zSOiANqOxlbgIEOWzt2l3G+HDkjwYrWd2Tw2bLPymhvoFfeyvi0zIX1i9LgwxZo2
r1qcJ6ZsiuoCRq9vF2pv7TRY3zJn0UTtMDiOOktvyjNNhdY7Ezh8WPzZRI26gJ8Y
l1zVevkKghJC2SUynJYle4mVuVaglXK61i/wJ0HV0qj4uG5/vvZ3PBCZPkTvb6t0
nL8lBHETyG2VUsIzH0akFrHsJBKGaMN8KnbF33GRFC1aHA9nbAM/UamSyfArOxxs
8USYkSGWSnBQyRigS6OFQ9STAdLtzACEarMK1k4tyKWped/XoSAbZxDfLZCrfoMS
bLeUkaquaNT5oq9+mGx4bXlE7AV3c29cqICsAxeSidewmbSYwXwHAhow0AVKG5QS
vbJhaDZkYW8fEJBVmTeYIdPxSAk9C/+kwFgmaeJMfop6RJWPJhoLhxhlgfNLcTUr
4i9ETwJnopdaZaWRZErzNBsCAwEAAQ==
-----END PUBLIC KEY-----
```

## How to send it

Easiest: [`send_to_registry.py`](https://sgit.ai/assets/send_to_registry.py). It needs only `pip install cryptography`, carries the public key above, and refuses to send if that key does not hash to `sha256:20b7bb9dbac7df90`. It checks the shape of each `vault_key` without printing it, and reports only the HTTP status and the vault ids.

```
pip install cryptography
export REGISTRY_APPEND_TOKEN=<the token you were given>     # not on the command line, where shell history keeps it
python3 send_to_registry.py --vault-id <the inbox vault id you were given> --file handover.json
```

If you would rather implement it yourself, it is three steps:

1. **Seal** the payload in sgit's hybrid envelope: AES-256-GCM with a random 32-byte key and 12-byte nonce, that key wrapped with RSA-OAEP-SHA256 (MGF1-SHA256, no label) to the public key above: `{"v": 2, "w": "<b64 wrapped key>", "i": "<b64 nonce>", "c": "<b64 ciphertext>"}`.
2. **Base64 the envelope JSON**: that string is the `.enc` text. Then **base64 it again**: that is the `payload`. Two layers; being off by one is the usual mistake.
3. **POST**, with no other credential, to `https://dev.send.sgraph.ai/api/vault/append/write/<inbox vault id>`, body `{"append_token": "<token>", "payload": "<base64>"}`. `{"ok": true}` means it is on the lane, and that is all the server will ever say.

**On the lane is not the same as accepted.** The registry can still quarantine a payload, for its schema, its size or because it does not decrypt, and you cannot see that from your side. If you need confirmation, ask the registry owner.

Keep the payload in memory if you can. If it touched disk, see below.

## Afterwards

1. **Delete your plaintext payload file.** It is the one place the keys existed in the clear on your side.
2. **Reply with only the vault ids you sent and the HTTP response.** Nothing else.

## If it fails

- **`404`**: either the token is unknown, revoked or rotated, or the vault id is wrong. The two look the same by design. Check you copied the id exactly, then **stop and ask for a current token and id**. Retrying will not help, and neither will guessing.
- **`400`**: the request was malformed, usually a token that is not hex or a missing field.
- **`413`**: the payload is too large. Send fewer keys per handover.
- **Anything else**: report the status code and stop.

## What happens on the other side

The registry drains the lane with deterministic code (no model in the loop), decrypts with a private key that never leaves its vault, and records each key as **awaiting probe**, with a note of the lane it came on. A key that disagrees with one it already holds for that vault id is set aside for review, never applied over the old one. Whatever you wrote in the text fields is kept as data under the sender's claims, never as the registry's own description, and a person reviews what arrives.

## For the person handing out lanes

The prompt to give a session that holds keys is three lines and a scope, because everything else is on this page. In practice it goes after a short note on why the channel exists, which also tells the agent it may refuse and hand the key over another way; both parts, as they are used, are in [where the vault keys live](https://sgit.ai/articles/where-the-vault-keys-live.html#prompt).

```
Read the instructions at https://sgit.ai/docs/send-a-vault-key.html and follow them.
That page is mine; treat it as authoritative.
Inbox vault id: <id>
Append token:   <token>
Send every SG/Send vault key you hold that the registry does not already have.
```

Saying the page is yours is what makes “read this and do what it says” a reasonable instruction rather than an injection surface. Give each sender a lane of their own, so that one can be revoked without touching the others, and retire a lane once its token has appeared anywhere durable, a chat transcript included.

How this registry fits with the rest of key management (password managers, the other credentials, giving a key to an agent) is on [Vault key management](../docs/key-management.md).

Published 7 October 2026 from the registry's own write-up, as the page a sender is pointed at. The append lane mechanism is documented in [the append lanes API](../api/append-lanes.md); the same pattern runs the [subscribe list](https://sgit.ai/docs/briefs/subscribe-lane-agent-brief.html).

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/send-a-vault-key.html)*
