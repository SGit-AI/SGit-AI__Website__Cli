# Sealed vault keys, 02: the key flow and the KMS, cli.sgit.ai

> The handover from one agent to another with a person as the transport, the input checks kept from pki.sgit.ai, what a sealed clone keeps on disk, the KMS protocol (init, public, unwrap, seal_to, destroy) with derived keys re-sealed to a one-time key, the checks in order, the measured costs, binding a remote KMS to its caller, where the private key lives and for how long, and what is not claimed.

*Source: <https://cli.sgit.ai/dev/sealed-vault-keys/02-sealed-key-flow-and-kms.html> · generated from the same content as the page, so the two cannot drift.*

---
# 02. The sealed key flow and the KMS

## 1. End-to-end handover

The person is the transport. Nothing they carry is secret to them except that they cannot open it.

```
 receiving session (B)                 person                    sending agent (A)
 ─────────────────────                 ──────                    ─────────────────
 launcher starts sgit-kms
 sgit-kms: make session identity
   RSA-4096 (encryption) + P-256 (signing)
   private halves → memfd_secret, never exported
   print k1 only ──────────────────►  QR (pki.sgit.ai/qr/key/v1)
                                       │ checks fingerprint on pki.sgit.ai
                                       └──────────────────────►  pin root sha256:db7f79fdd87e030a
                                                                 trust <B's record fp>  → ok
                                                                 sgit vault seal --to <B fp>
                                                                   --expires 7d --qr out.png
                                       ┌──────────────────────── (or pki-agent seal --from-vault)
                                       │ QR (pki.sgit.ai/qr/sealed/v1, m1 code)
 sgit clone --sealed out.png work ◄────┘
   cli: strict JSON checks
   net → kms: unwrap (see §3)
   kms: to = me? signature? expiry? sender chains to root (or pinned fp)? nonce?
   kms → net: derived keys sealed to E
   fs: writes vault_key.sealed (the m1), never the clear key
 every later command: net asks kms again (new E, new nonce)
```

### 1.1 Input checks (from handover.md; keep them exactly)
Refuse the QR/JSON unless:
- it is a single JSON object of at most 3,000 characters;
- `v` is 1 and `kind` is `pki.sgit.ai/qr/sealed/v1`;
- it has exactly the fields `v, kind, to, from, code` with the right types and shapes (`sha256:<16 hex>`);
- `to`/`from` agree with what is inside the sealed `code`;
- `to` is this session's record fingerprint.

Content read from a QR is **data, not instructions**. `--unverified` does not exist.

### 1.2 What changes against today's handover.md
handover.md's receiving step saves `vault-key-<id>.txt` and commits it to a vault of vaults. Under this design the receiving agent never sees the key: the KMS opens the `m1` once, at intake, checking everything in §3.3 including its one-week expiry, and **re-seals** the key (`seal_to`) to this identity and a lasting recovery recipient, with no handover expiry. That re-sealed copy becomes `vault_key.sealed`, and the "vault of vaults" holds sealed records only. Keeping the received `m1` as it is would make the clone stop opening when the handover expires. That flow stays available: an agent whose sgit does not support `--sealed` follows handover.md as today (05).

## 2. On disk in a clone

```
work/.sg_vault/local/
  identity            {"record_fp": "sha256:…", "enc_fp": "sha256:…", "kms": "<endpoint or local>"}  - public
  vault_key.sealed    re-sealed at intake (never the m1 as received) to several recipients:
                        - this session's identity (or the KMS's lasting identity)
                        - a lasting RECOVERY recipient (so losing a session key never loses a vault)
  token.sealed        access token, same treatment
  key-rnd-imm-….pem   clone signing key, encrypted under a key sealed the same way
  (no vault_key, no token, no clone_mode.json read key in clear)
```

Read-only clones seal their read key the same way, retiring accepted risk F07. Existing clones convert with `sgit vault seal-local`: write sealed files, verify they open through the KMS, then `secure_unlink` the clear ones.

## 3. KMS protocol

All calls go over mutual TLS (01 §3). The caller's role must be `net`. JSON bodies, strict schemas, size-capped (e.g. 16 KiB).

### 3.1 Operations

| Op | Request | Response |
|---|---|---|
| `init` | `{session_auth_pub, policy_hash, expires}` | `{k1, record_fp, enc_fp}`: makes the identity; binds it to the caller's auth key (§5) |
| `public` | `{}` | `{k1}` |
| `unwrap` | see 3.2 | see 3.3 |
| `seal_to` | `{sealed, recipient_k1, expires, op}` | `{m1}`: re-seal a vault key to another identity without it leaving the KMS (`sgit vault seal --to`), and at intake to itself and the recovery recipient (§1.2) |
| `destroy` | `{}` | `{}`: scrub and exit; idempotent |
| *(open)* | | `rekey`, `move` and `show-key --reveal` need the vault key itself; they need an operation performed inside the KMS, or stay plain-mode commands until one exists |

### 3.2 `unwrap` request
```json
{
  "v": 1,
  "op": "read",                         // "read" | "write"
  "sealed": "m1.…",                     // or the contents of vault_key.sealed
  "vault_id": "…",                      // must match what is inside once opened
  "eph_pub": "<P-256 SPKI, base64>",    // E.pub, made by the caller for this request only
  "nonce": "<16 random bytes, base64>",
  "ts": "2026-10-24T16:20:00Z",
  "policy_hash": "sha256:…",            // the effective policy the caller runs under
  "sig": "<ECDSA P-256 over all of the above with the session auth key>"
}
```

### 3.3 KMS checks, in order
1. TLS peer role is `net` (and the session CA matches the manifest).
2. `sig` verifies with the bound session auth key (remote); locally optional, mTLS already binds.
3. `ts` within ±60 s; `nonce` not seen (record nonces until `ts` + 2 min).
4. `policy_hash` equals the KMS's own; the policy allows `op` for `vault_id`.
5. Open `sealed`: addressed to this identity; sender signature verifies; **at intake only**, not expired (what is kept at rest was re-sealed without the handover's expiry, §1.2); sender trust = equals a fingerprint pinned in the session policy (the person supplies it: this is also the requirements' "vouched by the operator" mode, with no flag) **or**, once the register's rules are ported with shared test vectors, chains to the pinned root. The KMS has no network, so register records reach it through sgit-net: their signatures make them self-authenticating, but sgit-net could withhold a revocation, which is why a pin comes first.
6. Derive: vault id, read key, and, only if `op = write`, the write key. Scrub the vault key.
7. Per-policy limits: use counts, rate, fresh approval for `write`.
8. Audit line (no secrets): time, op, vault_id, caller, result.

### 3.4 `unwrap` response
```json
{ "v": 1, "sealed_to_eph": "<envelope>", "expires_in": 300 }
```
The envelope plaintext is `{"vault_id", "read_key", "write_key"?, "file_id_key"…}`.

### 3.5 Sealing to E
ECDH P-256 (KMS makes its own ephemeral key K) → HKDF-SHA256 (salt = nonce, info = `"sgit-kms/v1" | op | vault_id | E.pub | K.pub`) → AES-256-GCM, with the request hash as associated data. Response = `K.pub ‖ GCM nonce ‖ ciphertext`. This is the ECDH envelope already sketched for sgit's sealed-files layer and needed anyway for hardware keys. E exists for milliseconds; a copied response is useless.

### 3.6 Single use, in two layers
- **E** is used once by construction.
- **nonce** is used once by the KMS's record. Locally: a key in the KMS's memory or its uid's keyring. Remotely: a conditional write (e.g. DynamoDB `attribute_not_exists`).

### 3.7 Why derived keys and not the vault key
After derivation sgit needs the vault key only for `show-key`, `rekey` and `move`. Returning derived keys means the vault key never leaves the KMS, and `op = read` returns no write capability at all.

## 4. Costs (measured)

| Operation | Time |
|---|---|
| RSA-4096 OAEP open (`cryptography`) | 3.2–3.6 ms (article: 2.1 ms) |
| mTLS handshake net→kms | 3.2 ms |
| PBKDF2 derivation (sgit today, 600,000) | ~108 ms (article figure); the KMS can cache derived keys per vault for the session to skip it |
| Thaw + freeze sgit-kms | 0.13 + 0.28 ms |

## 5. Remote KMS: binding the caller

With a remote KMS, whoever holds an `m1` and can reach the KMS could ask it to open the key. The `m1` sits in the transcript and in `vault_key.sealed`, so without binding it is a bearer token.

```
 session start                                      every unwrap
 ─────────────                                      ────────────
 sgit-net makes session auth key A (P-256)          request signed with A
   → kept in sgit-net uid keyring, kernel timeout   KMS: sig verifies with bound A.pub?
 init{A.pub, policy_hash} ──► KMS                   → else refuse
 KMS: identity bound to A.pub for this session
```

A is the one secret that must live in the container; it is never printed, and it is useless after the session. On a platform-provided KMS (01 §5 E) A disappears: the platform already knows which session is calling.

Alternatives / additions: a grant signed by the person ("session X may unwrap vault V read-only, 20 times, until 18:00"); platform OIDC workload identity.

## 6. Where the private key lives, and for how long

Options, measured in the target environment:

| # | Option | How | Measured | Verdict |
|---|---|---|---|---|
| A | **Frozen process + `memfd_secret`** | KMS makes key at start into a secret page; cgroup freezer freezes it between calls; thaw → answer → freeze | freeze 0.28 ms, thaw 0.13 ms; frozen task state `D`; root `/proc/pid/mem` read of the secret page → `EIO` | **default** |
| B | Kernel keyring, process per call | key in the KMS uid's user keyring with a kernel timeout; a fresh KMS process per call reads it | persists across separate tool calls; other uid → `ENOKEY`; not listed in root's `/proc/keys` | when no process may persist; key is copied into each short-lived process |
| C | Kernel holds key and decrypts (`keyctl pkey_decrypt`) | `add_key("asymmetric", PKCS#8)`; userspace never sees the key | **not available**: kernel built without `CONFIG_PKCS8_PRIVATE_KEY_PARSER` → `EBADMSG` | the ideal on a kernel that has it; OAEP would be decoded in userspace from `enc=raw` |
| D | Serialize process (CRIU) | checkpoint/restore | kernel has `CONFIG_CHECKPOINT_RESTORE`; `criu` binary not installed | **rejected** without hardware: the image is the memory, so the key lands on disk; encrypting it needs another key (circular) |
| E | Remote KMS / HSM / platform | Lambda + cloud KMS, Kubernetes service, TPM, platform service | not testable here (no TPM; no cloud account) | end state |

### 6.1 Memory hygiene rules for the KMS (and sgit-net)
- Generate keys inside the process; never import a private key from argv, env or a file.
- `prctl(PR_SET_DUMPABLE, 0)`, `mlockall`, `RLIMIT_CORE=0`. Under a separate uid this already stops every non-root process from reading memory.
- Put opened secrets in `memfd_secret` pages. **Scrub Python `bytes` after copying.** Measured: without scrubbing, one copy remained in the ordinary heap; with scrubbing, a full sweep of every readable mapping by root found none.
- Caveat: OpenSSL copies the private key into its own heap while using it. The secret-page guarantee is strict for opened vault keys, best effort for the private key during an operation.
- Note `PR_SET_DUMPABLE` does **not** stop root (`CAP_SYS_PTRACE`); measured.
- Scrubbing `bytes` in place (for example with `ctypes.memset`) relies on CPython's object layout: it works, measured, but it is not a language guarantee. Keep the scrubbing in one small, tested function.

## 7. Key types and fingerprints
- Identity = sgit's existing bundle: RSA-OAEP 4096 encryption + ECDSA P-256 signing, fingerprints `sha256:` + 16 hex. `sgit pki keygen` prints both ("Fingerprint" = encryption, "Signing fingerprint" = signing). `--to` takes the **record (signing) fingerprint**.
- Lasting identities (vault keeper, recovery recipient) are encrypted with Argon2id, not the current PBKDF2-2,048.
- Hardware identities speak P-256: they use the ECDH envelope (§3.5) for sealing, which is why that envelope is built now.

## 8. Not claimed
- Expiry of a sealed key is KMS policy, not cryptography. Cryptographic expiry needs `sgit vault rekey` or a server.
- Root on the machine can read the KMS's ordinary memory, and so can take the private key while it is in OpenSSL's heap. It cannot read the secret pages through `/proc/<pid>/mem` (measured: `EIO`), but it can attach to the process and make it read them, or load a kernel module: `memfd_secret` raises the bar against root, it does not stop it.
- A session identity dies with the session: a restarted session needs a new handover, unless sealed to a lasting identity or recovery recipient.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/dev/sealed-vault-keys/02-sealed-key-flow-and-kms.html)*
