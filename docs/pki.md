# Keys, signatures and encrypting to someone else, cli.sgit.ai

> The keypair lifecycle run end to end on the shipped CLI: RSA-OAEP 4096 encryption, ECDSA P-256 signing, the JSON public-key bundle, the hybrid envelope format, and what PKI does not do yet.

*Source: <https://cli.sgit.ai/docs/pki.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/pki.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Keys, signatures and encrypting to someone else

The vault key is symmetric and opens the whole vault. A keypair does the two things it cannot: prove *who* wrote something, and encrypt to somebody who holds no vault key at all. This page is the lifecycle, run end to end on the shipped CLI.

**Everything below was executed, not recalled.** Every command, every output shape and every construction on this page came from running `sgit pki` on **v0.15.0** in a throwaway home directory. Where the behaviour differs from what you might expect, and in two places it does, the page says so.

## What sgit actually generates

`sgit pki keygen` creates **two** pairs at once, and prints two fingerprints:

| Purpose | Construction | Identifier |
|---|---|---|
| Encryption | **RSA-OAEP, 4096-bit** | `fingerprint` |
| Signing | **ECDSA P-256** | `signing_fingerprint` |

Encryption is **hybrid**, which is what makes it usable on files of any size: a fresh AES-256-GCM content key encrypts the payload, and RSA-OAEP wraps that content key. The same AES-256-GCM primitive as the rest of the vault, the keypair only changes how the content key gets to the recipient.

Note for anyone integrating against a spec rather than the binary: this is **RSA-OAEP and ECDSA**, not X25519/Ed25519. Draft material describing an X25519 sealing layer describes a design, not what v0.15.0 ships.

## The lifecycle

### 1 · Generate

```
$ sgit pki keygen --label "My Vault Identity"
Enter passphrase to protect private keys:

Generating RSA-4096 encryption key... done

Key pair created:
  Label:                My Vault Identity
  Encryption:           RSA-OAEP 4096-bit
  Signing:              ECDSA P-256
  Fingerprint:          sha256:a4615402a0bc23ac
  Signing fingerprint:  sha256:69d9b4835ccf790c
```

**Keygen prompts for a passphrase** and will not proceed without one, private keys are encrypted at rest. In a script, feed it on stdin; with no terminal at all it exits with an `EOFError` rather than silently generating an unprotected key, which is the right failure.

RSA-4096 generation is not instant. Expect a pause.

### 2 · Publish the public half

```
$ sgit pki list
  sha256:a4615402a0bc23ac  My Vault Identity  (RSA-OAEP 4096)

$ sgit pki export sha256:a4615402a0bc23ac > my-identity.json
```

**Export produces a JSON bundle, not a PEM file.** It carries both public keys, both fingerprints and the label:

```
{
  "v": 1,
  "encrypt": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkq…",
  "sign":    "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQ…",
  "label":   "My Vault Identity",
  "fingerprint":         "sha256:a4615402a0bc23ac",
  "signing_fingerprint": "sha256:69d9b4835ccf790c"
}
```

The bundle contains no private material. Publish it, mail it, commit it, put it on your website.

### 3 · Import someone else’s

```
$ sgit pki import their-identity.json
Imported contact: Their Label
  Fingerprint: sha256:…

$ sgit pki contacts
  sha256:…  Their Label
```

### 4 · Encrypt to them, and decrypt what they send you

```
$ sgit pki encrypt message.txt --recipient sha256:a4615402a0bc23ac
Encrypted to message.txt.enc

$ sgit pki decrypt message.txt.enc --fingerprint sha256:a4615402a0bc23ac
Enter passphrase:
Decrypted to message.txt
```

Round trip verified. Two argument details that will bite you once each: `encrypt` takes `--recipient` (a contact’s fingerprint) and an optional `--fingerprint` for *your* signing key; `decrypt` requires `--fingerprint`. It will not guess which of your keys to try.

### 5 · Sign and verify

```
$ sgit pki sign report.pdf --fingerprint sha256:69d9b4835ccf790c
$ sgit pki verify report.pdf report.pdf.sig
```

Detached signatures, so the signed file is unchanged. Signing uses the *signing* fingerprint, which is the second one keygen printed.

## The envelope on the wire

An encrypted file is base64 over a small JSON object, worth knowing if you are writing an interoperable client:

| Field | Contents | Observed size |
|---|---|---|
| `v` | Envelope version, `2` on v0.15.0 | none |
| `w` | The AES content key, wrapped with RSA-OAEP to the recipient | 512 bytes (4096-bit) |
| `i` | AES-GCM IV | 12 bytes |
| `c` | Ciphertext with its GCM tag | plaintext + 16 |
| `f` | The signer's fingerprint, when `encrypt` was given `--fingerprint` | none |
| `s` | The ECDSA signature, over `c` only | none |

**Two things to know when you rely on the signature** (checked 26 September 2026, on sgit-ai v0.16.0). First, **it covers the inner ciphertext `c` only**: not the wrapped key `w`, not the IV, and not who the message was encrypted to. Someone holding the recipient's private key could re-wrap a signed `c` to a third party. Signing the whole envelope is the recommended fix. Second, **`decrypt` reports the signer's label, not its fingerprint**, and only when the signer's bundle is in your keyring. Labels are not unique, so when identity matters, verify `s` against the expected key by fingerprint yourself. Both are from [the append-lane write-up](../docs/append-lane-messaging.md).

A 37-byte plaintext produced a 1,076-byte file: the RSA-wrapped key dominates, so this is efficient for large payloads and heavy for tiny ones.

## Where public keys live in a vault

Vaults carry public PKI keys as immutable objects at `bare/keys/key-rnd-imm-*`, alongside the content store at `bare/data/obj-cas-imm-*`. They are public by construction, so nothing there needs protecting, which is exactly why a lane addressed by a public key can be written to by a stranger.

## What this is for

Signing and encrypting files is useful on its own. The larger use is [**vault-to-vault messaging**](../docs/vault-messaging.md): your public key becomes an address a stranger can write to, and your private key is the only thing that can read what arrives. That page composes this one with [append lanes](../api/append-lanes.md).

## What this does not do yet

- **No key revocation or rotation workflow.** There is no CRL, no expiry, no `sgit pki revoke`. If a private key is compromised, you generate a new pair and redistribute the bundle out of band.
- **No web of trust and no directory.** Fingerprint verification is your problem, compare out of band, exactly as with SSH host keys.
- **Fingerprints carry a `sha256:` prefix.** That prefix is part of the CLI identifier, not part of any hash you might need elsewhere. See the [addressing note](../docs/vault-messaging.md#addressing). It is a live source of confusion.
- **Signing and encryption are separate keys.** Passing the wrong fingerprint to the wrong verb fails; it does not fall back.

Honest edges belong on [the limitations page](../docs/limitations.md) too, and these are listed there.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/pki.html)*
